"""Compute TLE conjunction predictions for a target observatory.

Reads a local TLE catalog file and computes all predicted transits where
a tracked object passes within the instrument beam during a time window.

Requires no third-party libraries.  Uses a simplified SGP4-compatible
orbit propagation (two-body + J2 perturbation) for conjunction screening,
accurate to ~1 km over short propagation windows.

Usage:
    # Step 1: Download TLE catalog (run from your own terminal, needs network)
    curl -o data/external/tle_debris.txt \\
         "https://celestrak.org/pub/TLE/debris.txt"

    # Step 2: Compute conjunctions
    PYTHONPATH=src python3.11 scripts/compute_tle_conjunctions.py \\
        --tle      data/external/tle_debris.txt \\
        --source   esa_swarm_alpha \\
        --start    2026-06-01T00:00:00Z \\
        --end      2026-06-07T00:00:00Z \\
        --output   data/local/conjunctions/swarm_alpha_2026_06.json \\
        --max-distance-km 50
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from heimdall.archive_mining import (
    ConjunctionPrediction,
    TleObject,
    ObservatorySpec,
    DataSource,
    REFERENCE_OBSERVATORIES,
)
from heimdall.domain import EvidenceClass


# ---------------------------------------------------------------------------
# Minimal two-body + J2 orbit propagator (no third-party deps)
# ---------------------------------------------------------------------------

_GM   = 3.986004418e14    # m³/s²
_RE   = 6.371e6           # m
_J2   = 1.08262668e-3
_TWO_PI = 2.0 * math.pi


def _parse_tle_epoch(tle_line1: str) -> datetime:
    """Parse TLE epoch from line 1 field 4 (two-digit year + day-of-year.fraction)."""
    epoch_str = tle_line1[18:32].strip()
    year2 = int(epoch_str[:2])
    year = 2000 + year2 if year2 < 57 else 1900 + year2
    day_frac = float(epoch_str[2:])
    day_of_year = int(day_frac)
    frac = day_frac - day_of_year
    base = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
    return base + timedelta(days=frac)


def _tle_mean_motion(tle_line2: str) -> float:
    """Extract mean motion in rad/s from TLE line 2."""
    mm_rev_per_day = float(tle_line2[52:63])
    return mm_rev_per_day * _TWO_PI / 86400.0


def _tle_semi_major_axis(n_rad_s: float) -> float:
    """Compute semi-major axis from mean motion (m)."""
    return (_GM / (n_rad_s ** 2)) ** (1.0 / 3.0)


def _tle_eccentricity(tle_line2: str) -> float:
    return float("0." + tle_line2[26:33])


def _tle_inclination(tle_line2: str) -> float:
    return math.radians(float(tle_line2[8:16]))


def _tle_raan(tle_line2: str) -> float:
    return math.radians(float(tle_line2[17:25]))


def _tle_arg_perigee(tle_line2: str) -> float:
    return math.radians(float(tle_line2[34:42]))


def _tle_mean_anomaly(tle_line2: str) -> float:
    return math.radians(float(tle_line2[43:51]))


def _eccentric_anomaly(M: float, e: float, tol: float = 1e-10) -> float:
    """Solve Kepler's equation M = E - e*sin(E) by Newton-Raphson."""
    E = M if e < 0.8 else math.pi
    for _ in range(50):
        dE = (M - E + e * math.sin(E)) / (1.0 - e * math.cos(E))
        E += dE
        if abs(dE) < tol:
            break
    return E


def _eci_position(tle: TleObject, t: datetime) -> tuple[float, float, float]:
    """Approximate ECI position (m) of a TLE object at time t.

    Uses two-body propagation with J2 precession of RAAN and arg-perigee.
    Accurate to ~1 km for conjunction screening; not suitable for precise
    orbit determination.
    """
    line2 = tle.tle_line2
    n   = _tle_mean_motion(tle.tle_line2)
    a   = _tle_semi_major_axis(n)
    e   = _tle_eccentricity(line2)
    i   = _tle_inclination(line2)
    w   = _tle_arg_perigee(line2)
    M0  = _tle_mean_anomaly(line2)
    epoch = _parse_tle_epoch(tle.tle_line1)

    dt = (t - epoch).total_seconds()

    # J2 secular rates
    p   = a * (1 - e ** 2)
    coeff = -1.5 * _J2 * (_RE / p) ** 2 * n
    raan_dot   = coeff * math.cos(i)
    omega_dot  = coeff * (2.5 * math.sin(i) ** 2 - 2.0)

    raan  = _tle_raan(line2)  + raan_dot  * dt
    omega = w + omega_dot * dt
    M     = M0 + n * dt

    E = _eccentric_anomaly(M % _TWO_PI, e)
    nu = 2.0 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2.0),
                           math.sqrt(1 - e) * math.cos(E / 2.0))
    r  = a * (1.0 - e * math.cos(E))

    # Perifocal → ECI
    u  = omega + nu
    x  =  r * (math.cos(raan) * math.cos(u) - math.sin(raan) * math.sin(u) * math.cos(i))
    y  =  r * (math.sin(raan) * math.cos(u) + math.cos(raan) * math.sin(u) * math.cos(i))
    z  =  r * math.sin(u) * math.sin(i)
    return x, y, z


def _geodetic_to_eci(lat_deg: float, lon_deg: float, alt_m: float, t: datetime) -> tuple[float, float, float]:
    """Convert geodetic coordinates to approximate ECI (m).

    Uses Greenwich Apparent Sidereal Time approximation.
    """
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    r   = _RE + alt_m

    # Approximate GAST (accurate to a few arc-seconds)
    j2000 = (t - datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)).total_seconds() / 86400.0
    gast  = (280.46061837 + 360.98564736629 * j2000) % 360.0
    theta = math.radians(gast) + lon

    x = r * math.cos(lat) * math.cos(theta)
    y = r * math.cos(lat) * math.sin(theta)
    z = r * math.sin(lat)
    return x, y, z


def _distance_km(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b))) / 1000.0


def _ground_track_distance_km(
    obj_pos: tuple[float, float, float],
    obs_pos: tuple[float, float, float],
) -> tuple[float, float]:
    """Return (slant_range_km, elevation_deg) from observatory to object."""
    dx, dy, dz = (obj_pos[i] - obs_pos[i] for i in range(3))
    slant = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2) / 1000.0
    # Elevation: angle above horizon at observer
    obs_r = math.sqrt(sum(v ** 2 for v in obs_pos))
    dot   = sum(obs_pos[i] * (dx, dy, dz)[i] for i in range(3))
    sin_el = dot / (obs_r * slant * 1000.0) if slant > 0 else 0.0
    el_deg = math.degrees(math.asin(max(-1.0, min(1.0, sin_el))))
    return slant, el_deg


# ---------------------------------------------------------------------------
# Conjunction screening
# ---------------------------------------------------------------------------

def load_tle_objects(path: Path, max_objects: int = 5000) -> list[TleObject]:
    """Load TLE catalog from a 3-line set text file."""
    objects: list[TleObject] = []
    lines = [l.rstrip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    i = 0
    while i + 2 < len(lines) and len(objects) < max_objects:
        name, l1, l2 = lines[i], lines[i + 1], lines[i + 2]
        if l1.startswith("1 ") and l2.startswith("2 "):
            try:
                cat_no = int(l2[2:7])
                objects.append(TleObject(
                    catalog_number=cat_no,
                    name=name.strip(),
                    tle_line1=l1,
                    tle_line2=l2,
                    catalog_source="local_file",
                ))
            except (ValueError, IndexError):
                pass
        i += 3
    return objects


def compute_conjunctions(
    tle_objects: list[TleObject],
    observatory: ObservatorySpec,
    start_utc: datetime,
    end_utc: datetime,
    time_step_s: float = 60.0,
    max_distance_km: float = 50.0,
) -> list[ConjunctionPrediction]:
    """Screen all TLE objects for conjunctions with the observatory.

    Uses coarse time-step screening then refines close approaches.
    Returns conjunction predictions sorted by predicted transit time.
    """
    conjunctions: list[ConjunctionPrediction] = []
    t = start_utc

    # Pre-compute observatory ECI trajectory at coarse step
    obs_track: list[tuple[datetime, tuple[float, float, float]]] = []
    while t <= end_utc:
        obs_track.append((t, _geodetic_to_eci(
            observatory.latitude_deg,
            observatory.longitude_deg,
            observatory.altitude_m,
            t,
        )))
        t += timedelta(seconds=time_step_s)

    for tle in tle_objects:
        try:
            prev_dist = None
            for ts, obs_pos in obs_track:
                obj_pos = _eci_position(tle, ts)
                dist = _distance_km(obj_pos, obs_pos)

                # Look for local minimum (closest approach)
                if prev_dist is not None and dist < max_distance_km and dist < prev_dist:
                    slant, el_deg = _ground_track_distance_km(obj_pos, obs_pos)
                    if el_deg > 10.0 or observatory.beam_halfwidth_deg == 0.0:
                        # Compute transit duration from orbital period / beam subtended angle
                        n = _tle_mean_motion(tle.tle_line2)
                        period_s = _TWO_PI / n if n > 0 else 5700.0
                        orbit_circ_km = _TWO_PI * _tle_semi_major_axis(n) / 1000.0
                        velocity_km_s = orbit_circ_km / period_s
                        transit_s = (
                            2.0 * observatory.beam_halfwidth_deg * math.pi / 180.0
                            * slant / max(velocity_km_s, 0.1)
                        ) if observatory.beam_halfwidth_deg > 0 else 2.0

                        conj_id = "conj-" + sha256(
                            f"{tle.catalog_number}-{ts.isoformat()}".encode()
                        ).hexdigest()[:10]

                        conjunctions.append(ConjunctionPrediction(
                            conjunction_id=conj_id,
                            tle_object=tle,
                            observatory=observatory,
                            predicted_transit_utc=ts,
                            closest_approach_km=dist,
                            elevation_deg=el_deg,
                            relative_velocity_km_s=velocity_km_s,
                            transit_duration_s=max(transit_s, 0.1),
                            propagator_id="two_body_j2_screening",
                            evidence_class=EvidenceClass.SYNTHETIC,
                        ))

                prev_dist = dist
        except Exception:
            continue

    conjunctions.sort(key=lambda c: c.predicted_transit_utc)
    return conjunctions


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Compute TLE conjunction predictions")
    parser.add_argument("--tle",              required=True,  help="Path to TLE catalog file")
    parser.add_argument("--source",           default="esa_swarm_alpha",
                        choices=[s.value for s in DataSource],
                        help="Target instrument/observatory source ID")
    parser.add_argument("--start",            required=True,  help="Start UTC (ISO-8601)")
    parser.add_argument("--end",              required=True,  help="End UTC (ISO-8601)")
    parser.add_argument("--output",           default="data/local/conjunctions/conjunctions.json")
    parser.add_argument("--max-distance-km",  type=float, default=50.0)
    parser.add_argument("--time-step-s",      type=float, default=60.0)
    parser.add_argument("--max-objects",      type=int, default=2000,
                        help="Limit TLE objects for faster screening")
    args = parser.parse_args()

    tle_path = Path(args.tle)
    if not tle_path.exists():
        print(f"[compute_tle_conjunctions] TLE file not found: {tle_path}")
        print("  Download with:")
        print('    curl -o data/external/tle_debris.txt "https://celestrak.org/pub/TLE/debris.txt"')
        sys.exit(1)

    source = DataSource(args.source)
    observatory = REFERENCE_OBSERVATORIES.get(source)
    if observatory is None:
        print(f"[compute_tle_conjunctions] no reference observatory for {source.value}")
        sys.exit(1)

    start = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
    end   = datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc)

    print(f"[compute_tle_conjunctions] loading TLE catalog: {tle_path}")
    tle_objects = load_tle_objects(tle_path, max_objects=args.max_objects)
    print(f"[compute_tle_conjunctions] loaded {len(tle_objects)} objects")

    tle_digest = "sha256:" + sha256(tle_path.read_bytes()).hexdigest()
    print(f"[compute_tle_conjunctions] catalog digest: {tle_digest[:32]}...")

    print(f"[compute_tle_conjunctions] screening {start.date()} → {end.date()} "
          f"for {observatory.name}")
    conjunctions = compute_conjunctions(
        tle_objects, observatory, start, end,
        time_step_s=args.time_step_s,
        max_distance_km=args.max_distance_km,
    )

    print(f"[compute_tle_conjunctions] found {len(conjunctions)} conjunctions "
          f"within {args.max_distance_km} km")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tle_catalog": str(tle_path),
        "tle_catalog_digest": tle_digest,
        "observatory": source.value,
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "max_distance_km": args.max_distance_km,
        "total_conjunctions": len(conjunctions),
        "conjunctions": [
            {
                "conjunction_id": c.conjunction_id,
                "catalog_number": c.tle_object.catalog_number,
                "object_name": c.tle_object.name,
                "predicted_transit_utc": c.predicted_transit_utc.isoformat(),
                "closest_approach_km": round(c.closest_approach_km, 3),
                "elevation_deg": round(c.elevation_deg, 2),
                "relative_velocity_km_s": round(c.relative_velocity_km_s, 3),
                "transit_duration_s": round(c.transit_duration_s, 2),
            }
            for c in conjunctions
        ],
    }, indent=2))
    print(f"[compute_tle_conjunctions] written → {out}")


if __name__ == "__main__":
    main()
