"""Digital signal processing for passive ionospheric debris detection.

Provides composable, plug-and-play DSP building blocks:
    - CrossCorrelation: TDOA from two time-series (pure Python FFT via DFT)
    - MatchedFilter: coherent detection against a template
    - PowerSpectralDensity: Welch/periodogram estimators
    - WindowFunction: tapering windows for spectral leakage control

Design:
    Every algorithm is:
    1. Stateless — takes immutable input, returns immutable output
    2. Protocol-typed — every abstraction layer has a Protocol interface
    3. Type-safe — 100% type hint coverage
    4. Failure-bounded — raises ValueError on invalid input, never silently continues
    5. Pure Python — no numpy/scipy; all FFT via Cooley-Tukey DFT implementation

    To substitute a numpy-backed implementation:
        class NumpyCrossCorrelation:
            algorithm_id = "numpy_fft_xcorr"
            def correlate(self, x, y, sample_rate_hz) -> CorrelationResult: ...
        # Register via AdapterRegistry — zero pipeline changes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol, Sequence


# ---------------------------------------------------------------------------
# Core DFT — Cooley-Tukey radix-2 FFT (pure Python)
# ---------------------------------------------------------------------------

def _fft(x: list[complex]) -> list[complex]:
    """Cooley-Tukey radix-2 FFT. Input length must be a power of 2."""
    n = len(x)
    if n <= 1:
        return list(x)
    if n & (n - 1):
        raise ValueError(f"FFT input length must be a power of 2, got {n}")
    even = _fft(x[0::2])
    odd  = _fft(x[1::2])
    w = [complex(math.cos(-2 * math.pi * k / n), math.sin(-2 * math.pi * k / n)) for k in range(n // 2)]
    return [even[k] + w[k] * odd[k] for k in range(n // 2)] + \
           [even[k] - w[k] * odd[k] for k in range(n // 2)]


def _ifft(x: list[complex]) -> list[complex]:
    """Inverse FFT via conjugate symmetry."""
    n = len(x)
    conj = [c.conjugate() for c in x]
    result = _fft(conj)
    return [c.conjugate() / n for c in result]


def _next_power_of_2(n: int) -> int:
    p = 1
    while p < n:
        p <<= 1
    return p


def _zero_pad(x: Sequence[float], length: int) -> list[complex]:
    return [complex(v, 0.0) for v in x] + [0j] * (length - len(x))


# ---------------------------------------------------------------------------
# Window functions
# ---------------------------------------------------------------------------

class WindowFunction(Protocol):
    """A tapering window for spectral leakage control."""
    window_id: str
    def apply(self, n: int) -> tuple[float, ...]: ...


@dataclass(frozen=True)
class RectangularWindow:
    """No tapering — equivalent to boxcar window."""
    window_id: str = "rectangular"
    def apply(self, n: int) -> tuple[float, ...]:
        return tuple(1.0 for _ in range(n))


@dataclass(frozen=True)
class HanningWindow:
    """Hanning (raised cosine) window — good frequency resolution."""
    window_id: str = "hanning"
    def apply(self, n: int) -> tuple[float, ...]:
        return tuple(0.5 * (1.0 - math.cos(2.0 * math.pi * i / max(n - 1, 1))) for i in range(n))


@dataclass(frozen=True)
class BlackmanWindow:
    """Blackman window — lower sidelobes than Hanning."""
    window_id: str = "blackman"
    def apply(self, n: int) -> tuple[float, ...]:
        return tuple(
            0.42 - 0.5 * math.cos(2 * math.pi * i / max(n - 1, 1))
                 + 0.08 * math.cos(4 * math.pi * i / max(n - 1, 1))
            for i in range(n)
        )


# ---------------------------------------------------------------------------
# Cross-correlation (TDOA)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CorrelationResult:
    """Output of a cross-correlation between two time series."""
    algorithm_id: str
    tdoa_s: float                  # time delay of arrival (s)  — positive means x2 lags x1
    peak_correlation: float        # normalised peak value in [-1, 1]
    peak_sample_index: int         # index of peak in correlation array
    correlation_values: tuple[float, ...]  # full correlation function
    sample_rate_hz: float
    n_samples: int
    snr_estimate_db: float         # peak / RMS of sidelobes (dB)
    confidence: float              # normalised peak height [0, 1]

    def __post_init__(self) -> None:
        if self.sample_rate_hz <= 0:
            raise ValueError("sample rate must be positive")

    @property
    def tdoa_samples(self) -> float:
        return self.tdoa_s * self.sample_rate_hz

    @property
    def tdoa_uncertainty_s(self) -> float:
        """Approximate TDOA uncertainty from CRB: σ_τ ≈ 1 / (2π × BW × SNR)."""
        bw = self.sample_rate_hz / 2.0
        snr_linear = 10.0 ** (self.snr_estimate_db / 10.0)
        return 1.0 / (2.0 * math.pi * bw * max(math.sqrt(snr_linear), 1e-6))


class CrossCorrelationAlgorithm(Protocol):
    algorithm_id: str
    def correlate(
        self,
        x1: Sequence[float],
        x2: Sequence[float],
        sample_rate_hz: float,
    ) -> CorrelationResult: ...


@dataclass(frozen=True)
class FftCrossCorrelation:
    """FFT-based cross-correlation for TDOA estimation.

    Normalised GCC (Generalised Cross-Correlation) without pre-filtering.
    For PHAT pre-filtering, use GccPhatCrossCorrelation.
    """
    algorithm_id: str = "fft_gcc"

    def correlate(
        self,
        x1: Sequence[float],
        x2: Sequence[float],
        sample_rate_hz: float,
    ) -> CorrelationResult:
        if len(x1) != len(x2):
            raise ValueError(f"x1 and x2 must have equal length, got {len(x1)} vs {len(x2)}")
        if len(x1) < 2:
            raise ValueError("signal must have at least 2 samples")
        if sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")

        n = len(x1)
        nfft = _next_power_of_2(2 * n - 1)

        X1 = _fft(_zero_pad(x1, nfft))
        X2 = _fft(_zero_pad(x2, nfft))

        # Cross-power spectrum: X1 * conj(X2)
        cross = [a * b.conjugate() for a, b in zip(X1, X2)]

        # Normalise: GCC-plain
        corr_complex = _ifft(cross)
        corr = [c.real for c in corr_complex]

        # Normalise to [-1, 1]
        norm = max(abs(corr[0]), 1e-12)
        norm_scale = math.sqrt(sum(v ** 2 for v in corr[:nfft // 2]))
        if norm_scale > 0:
            corr = [v / norm_scale for v in corr]

        # Shift to centred: lags from -(n-1) to +(n-1)
        # In the FFT convention, positive lags are at the beginning, negative at the end
        # Rearrange to: [-(n-1), ..., -1, 0, 1, ..., (n-1)]
        half = n - 1
        centred = corr[nfft - half:] + corr[:half + 1]

        peak_idx = max(range(len(centred)), key=lambda i: abs(centred[i]))
        peak_val = centred[peak_idx]
        lag_samples = peak_idx - half  # centred index → lag in samples
        tdoa_s = lag_samples / sample_rate_hz

        # SNR estimate: peak / RMS of remaining
        sidelobe_values = [abs(centred[i]) for i in range(len(centred)) if i != peak_idx]
        rms_sidelobe = math.sqrt(sum(v ** 2 for v in sidelobe_values) / max(len(sidelobe_values), 1))
        snr_db = 20.0 * math.log10(abs(peak_val) / max(rms_sidelobe, 1e-12))
        confidence = min(abs(peak_val), 1.0)

        return CorrelationResult(
            algorithm_id=self.algorithm_id,
            tdoa_s=tdoa_s,
            peak_correlation=peak_val,
            peak_sample_index=peak_idx,
            correlation_values=tuple(centred),
            sample_rate_hz=sample_rate_hz,
            n_samples=n,
            snr_estimate_db=snr_db,
            confidence=confidence,
        )


@dataclass(frozen=True)
class GccPhatCrossCorrelation:
    """GCC-PHAT — phase-only normalisation, sharp peak for broadband signals.

    PHAT (Phase Transform) whitens the cross-spectrum before IFFT:
        Ψ(ω) = X1(ω) × conj(X2(ω)) / |X1(ω) × conj(X2(ω))|
    This gives sharper peaks for wideband signals like plasma wake transients.
    """
    algorithm_id: str = "gcc_phat"

    def correlate(
        self,
        x1: Sequence[float],
        x2: Sequence[float],
        sample_rate_hz: float,
    ) -> CorrelationResult:
        if len(x1) != len(x2):
            raise ValueError(f"x1 and x2 must have equal length")
        if sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")

        n = len(x1)
        nfft = _next_power_of_2(2 * n - 1)
        X1 = _fft(_zero_pad(x1, nfft))
        X2 = _fft(_zero_pad(x2, nfft))

        cross = [a * b.conjugate() for a, b in zip(X1, X2)]
        # PHAT: divide by magnitude → phase only
        phat = [c / max(abs(c), 1e-30) for c in cross]
        corr_complex = _ifft(phat)
        corr = [c.real for c in corr_complex]

        half = n - 1
        centred = corr[nfft - half:] + corr[:half + 1]
        peak_idx = max(range(len(centred)), key=lambda i: abs(centred[i]))
        peak_val = centred[peak_idx]
        lag_samples = peak_idx - half
        tdoa_s = lag_samples / sample_rate_hz

        sidelobe_values = [abs(centred[i]) for i in range(len(centred)) if i != peak_idx]
        rms_sidelobe = math.sqrt(sum(v**2 for v in sidelobe_values) / max(len(sidelobe_values), 1))
        snr_db = 20.0 * math.log10(abs(peak_val) / max(rms_sidelobe, 1e-12))

        return CorrelationResult(
            algorithm_id=self.algorithm_id,
            tdoa_s=tdoa_s,
            peak_correlation=peak_val,
            peak_sample_index=peak_idx,
            correlation_values=tuple(centred),
            sample_rate_hz=sample_rate_hz,
            n_samples=n,
            snr_estimate_db=snr_db,
            confidence=min(abs(peak_val), 1.0),
        )


# ---------------------------------------------------------------------------
# Matched filter
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MatchedFilterResult:
    """Output of matched filter applied to one signal."""
    algorithm_id: str
    peak_score: float              # normalised peak [0, 1]
    peak_time_s: float             # time of peak in the input signal
    peak_sample_index: int
    scores: tuple[float, ...]      # full filter output
    sample_rate_hz: float
    detection_threshold: float
    detected: bool
    snr_db: float

    def __post_init__(self) -> None:
        if self.sample_rate_hz <= 0:
            raise ValueError("sample rate must be positive")


class MatchedFilterAlgorithm(Protocol):
    algorithm_id: str
    def filter(
        self,
        signal: Sequence[float],
        template: Sequence[float],
        sample_rate_hz: float,
        threshold: float,
    ) -> MatchedFilterResult: ...


@dataclass(frozen=True)
class FftMatchedFilter:
    """FFT-based matched filter — correlates signal against a template.

    The matched filter is the optimal linear filter in white Gaussian noise.
    The template is the expected signal waveform (e.g., a Gaussian transient).
    """
    algorithm_id: str = "fft_matched_filter"

    def filter(
        self,
        signal: Sequence[float],
        template: Sequence[float],
        sample_rate_hz: float,
        threshold: float = 0.5,
    ) -> MatchedFilterResult:
        if len(signal) < len(template):
            raise ValueError("signal must be at least as long as template")
        if sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        if not 0 < threshold < 1:
            raise ValueError("threshold must be in (0, 1)")

        n = len(signal)
        nfft = _next_power_of_2(n + len(template) - 1)

        # Matched filter = correlation with time-reversed template
        template_rev = list(reversed(template))
        S = _fft(_zero_pad(signal, nfft))
        H = _fft(_zero_pad(template_rev, nfft))
        output_complex = _ifft([s * h for s, h in zip(S, H)])
        output = [abs(c) for c in output_complex[:n]]

        # Normalise by template energy
        template_energy = math.sqrt(sum(t ** 2 for t in template))
        if template_energy > 0:
            output = [v / template_energy for v in output]

        # Normalise to [0, 1]
        max_val = max(output) if output else 1.0
        if max_val > 0:
            output_norm = [v / max_val for v in output]
        else:
            output_norm = output

        peak_idx  = max(range(len(output_norm)), key=lambda i: output_norm[i])
        peak_val  = output_norm[peak_idx]
        peak_time = peak_idx / sample_rate_hz

        sidelobes = [output_norm[i] for i in range(len(output_norm)) if i != peak_idx]
        rms_side  = math.sqrt(sum(v ** 2 for v in sidelobes) / max(len(sidelobes), 1))
        snr_db    = 20.0 * math.log10(peak_val / max(rms_side, 1e-12))

        return MatchedFilterResult(
            algorithm_id=self.algorithm_id,
            peak_score=peak_val,
            peak_time_s=peak_time,
            peak_sample_index=peak_idx,
            scores=tuple(output_norm),
            sample_rate_hz=sample_rate_hz,
            detection_threshold=threshold,
            detected=peak_val >= threshold,
            snr_db=snr_db,
        )


# ---------------------------------------------------------------------------
# Power spectral density
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PowerSpectrum:
    """Power spectral density estimate."""
    algorithm_id: str
    frequencies_hz: tuple[float, ...]
    power_db: tuple[float, ...]     # dB relative to full-scale
    sample_rate_hz: float
    n_samples: int
    frequency_resolution_hz: float
    peak_frequency_hz: float
    peak_power_db: float

    def __post_init__(self) -> None:
        if len(self.frequencies_hz) != len(self.power_db):
            raise ValueError("frequencies and power arrays must have equal length")

    def in_band(self, f_low_hz: float, f_high_hz: float) -> float:
        """Return integrated power in a frequency band (dB)."""
        band = [p for f, p in zip(self.frequencies_hz, self.power_db)
                if f_low_hz <= f <= f_high_hz]
        if not band:
            return -math.inf
        power_linear = sum(10.0 ** (p / 10.0) for p in band)
        return 10.0 * math.log10(max(power_linear, 1e-30))


@dataclass(frozen=True)
class PeriodogramEstimator:
    """Simple periodogram PSD estimator with selectable window."""
    algorithm_id: str = "periodogram"
    window: WindowFunction = RectangularWindow()

    def estimate(self, signal: Sequence[float], sample_rate_hz: float) -> PowerSpectrum:
        if len(signal) < 4:
            raise ValueError("signal must have at least 4 samples")
        if sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")

        n = len(signal)
        nfft = _next_power_of_2(n)
        win = self.window.apply(n)

        # Apply window and pad
        windowed = [float(signal[i]) * win[i] for i in range(n)]
        padded = _zero_pad(windowed, nfft)
        spectrum = _fft(padded)

        # One-sided PSD
        n_pos = nfft // 2 + 1
        psd = [abs(spectrum[k]) ** 2 / (sample_rate_hz * n) for k in range(n_pos)]
        # Double positive frequencies (one-sided)
        psd = [psd[0]] + [2.0 * v for v in psd[1:-1]] + [psd[-1]]
        freqs = [k * sample_rate_hz / nfft for k in range(n_pos)]

        psd_db = [10.0 * math.log10(max(v, 1e-40)) for v in psd]
        peak_idx = max(range(len(psd_db)), key=lambda i: psd_db[i])

        return PowerSpectrum(
            algorithm_id=self.algorithm_id,
            frequencies_hz=tuple(freqs),
            power_db=tuple(psd_db),
            sample_rate_hz=sample_rate_hz,
            n_samples=n,
            frequency_resolution_hz=sample_rate_hz / nfft,
            peak_frequency_hz=freqs[peak_idx],
            peak_power_db=psd_db[peak_idx],
        )
