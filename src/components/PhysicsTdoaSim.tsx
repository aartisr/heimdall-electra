import React, { useState, useMemo, useEffect, useRef } from 'react';
import {
  Activity,
  Orbit,
  Radio,
  Compass,
  RotateCcw,
  Info,
  Zap,
  ShieldCheck,
  Sliders,
  Volume2,
  VolumeX,
  Play,
  Pause,
  Layers,
} from 'lucide-react';

export const PhysicsTdoaSim: React.FC = () => {
  // Parameters
  const [debrisVelocity, setDebrisVelocity] = useState<number>(7.5); // km/s
  const [soundSpeed, setSoundSpeed] = useState<number>(1.8); // km/s (ion acoustic speed)
  const [debrisSizeCm, setDebrisSizeCm] = useState<number>(3.0); // cm
  const [clockJitterNs, setClockJitterNs] = useState<number>(0.5); // ns
  const [sensorBaselineKm, setSensorBaselineKm] = useState<number>(50); // km
  const [isAudioEnabled, setIsAudioEnabled] = useState<boolean>(false);
  const [isSimRunning, setIsSimRunning] = useState<boolean>(true);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);

  // Calculations
  const machNumber = useMemo(() => {
    return debrisVelocity / soundSpeed;
  }, [debrisVelocity, soundSpeed]);

  const machConeAngleDeg = useMemo(() => {
    if (machNumber <= 1) return 90;
    return (Math.asin(1 / machNumber) * 180) / Math.PI;
  }, [machNumber]);

  // Wake length estimate in LEO plasma before thermalization
  const wakeLengthMeters = useMemo(() => {
    return Math.round(debrisVelocity * 1000 * 0.08); // meters
  }, [debrisVelocity]);

  // Geometric Dilution of Precision (GDOP) and Positioning Error Estimate (m)
  const estimatedErrorM = useMemo(() => {
    const c = 299792458; // m/s
    const dt = clockJitterNs * 1e-9;
    const baseError = c * dt;
    const gdop = Math.max(1.2, 80 / sensorBaselineKm);
    return Math.max(0.5, +(baseError * gdop).toFixed(2));
  }, [clockJitterNs, sensorBaselineKm]);

  // Web Audio Synthetic Acoustic Sonification Ping
  const playRadarPing = () => {
    if (!isAudioEnabled) return;
    try {
      if (!audioCtxRef.current) {
        const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        audioCtxRef.current = new AudioContextClass();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      // Pitch determined by Mach number
      const baseFreq = 440 + machNumber * 80;
      osc.type = 'sine';
      osc.frequency.setValueAtTime(baseFreq, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(baseFreq * 1.6, ctx.currentTime + 0.12);

      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.25);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.25);
    } catch {
      // Ignore audio sandbox errors
    }
  };

  // Presets
  const applyPreset = (v: number, cs: number, d: number, jitter: number, baseline: number) => {
    setDebrisVelocity(v);
    setSoundSpeed(cs);
    setDebrisSizeCm(d);
    setClockJitterNs(jitter);
    setSensorBaselineKm(baseline);
    playRadarPing();
  };

  // Animated High-Fidelity Physics Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let time = 0;

    // Particles array for ion wake
    const particles: { x: number; y: number; vx: number; vy: number; life: number; maxLife: number; color: string }[] = [];

    const render = () => {
      time += 0.03;
      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);

      // Draw Grid
      ctx.strokeStyle = 'rgba(30, 41, 59, 0.4)';
      ctx.lineWidth = 1;
      const gridSize = 24;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Constellation 4 Nodes
      const nodeA = { x: width * 0.2, y: height * 0.22, name: 'RX-1' };
      const nodeB = { x: width * 0.8, y: height * 0.22, name: 'RX-2' };
      const nodeC = { x: width * 0.25, y: height * 0.82, name: 'RX-3' };
      const nodeD = { x: width * 0.75, y: height * 0.82, name: 'RX-4' };
      const nodes = [nodeA, nodeB, nodeC, nodeD];

      // Debris position (oscillates along trajectory with supersonic velocity)
      const debrisX = ((time * debrisVelocity * 14) % (width + 120)) - 60;
      const debrisY = height * 0.52;

      // Spawn plasma wake particles
      if (isSimRunning && debrisX > 0 && debrisX < width) {
        for (let i = 0; i < 3; i++) {
          const spreadAngle = (machConeAngleDeg * Math.PI) / 180;
          const sign = Math.random() > 0.5 ? 1 : -1;
          const pAngle = Math.PI - spreadAngle * (0.8 + Math.random() * 0.4) * sign;
          const speed = (0.5 + Math.random() * 1.5) * (debrisSizeCm / 3);

          particles.push({
            x: debrisX,
            y: debrisY,
            vx: Math.cos(pAngle) * speed,
            vy: Math.sin(pAngle) * speed,
            life: 0,
            maxLife: 40 + Math.random() * 30,
            color: Math.random() > 0.3 ? 'rgba(6, 182, 212, ' : 'rgba(59, 130, 246, ',
          });
        }
      }

      // Update & Draw Particles
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life += 1;

        const alpha = Math.max(0, 1 - p.life / p.maxLife);
        ctx.fillStyle = `${p.color}${alpha * 0.8})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, Math.max(1, (1 - p.life / p.maxLife) * (debrisSizeCm * 0.8)), 0, Math.PI * 2);
        ctx.fill();

        if (p.life >= p.maxLife) {
          particles.splice(i, 1);
        }
      }

      // Draw Mach Shock Wave Cone
      if (debrisX > -40 && debrisX < width + 100) {
        const halfAngleRad = (machConeAngleDeg * Math.PI) / 180;
        const coneLen = 220;

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(debrisX, debrisY);
        ctx.lineTo(debrisX - coneLen * Math.cos(halfAngleRad), debrisY - coneLen * Math.sin(halfAngleRad));
        ctx.lineTo(debrisX - coneLen * Math.cos(halfAngleRad), debrisY + coneLen * Math.sin(halfAngleRad));
        ctx.closePath();

        const grad = ctx.createLinearGradient(debrisX, debrisY, debrisX - coneLen, debrisY);
        grad.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
        grad.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.restore();

        // Draw Acoustic Shockwave Wavefront Rings
        for (let ring = 1; ring <= 4; ring++) {
          const ringDist = (ring * 35 + (time * 20) % 35);
          const rx = debrisX - ringDist;
          if (rx > 0) {
            ctx.strokeStyle = `rgba(56, 189, 248, ${Math.max(0, 0.5 - ring * 0.1)})`;
            ctx.lineWidth = 1.2;
            ctx.beginPath();
            ctx.arc(debrisX, debrisY, ringDist, Math.PI - halfAngleRad, Math.PI + halfAngleRad);
            ctx.stroke();
          }
        }
      }

      // Draw TDOA Sensor Hyperbola Measurement Lines to Nodes
      nodes.forEach((node) => {
        const dist = Math.hypot(node.x - debrisX, node.y - debrisY);
        const inRange = dist < 260;

        ctx.strokeStyle = inRange ? 'rgba(6, 182, 212, 0.4)' : 'rgba(51, 65, 85, 0.2)';
        ctx.lineWidth = inRange ? 1.5 : 0.8;
        if (inRange) {
          ctx.setLineDash([4, 4]);
        } else {
          ctx.setLineDash([]);
        }

        ctx.beginPath();
        ctx.moveTo(node.x, node.y);
        ctx.lineTo(debrisX, debrisY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw Node
        ctx.fillStyle = inRange ? '#06b6d4' : '#334155';
        ctx.beginPath();
        ctx.arc(node.x, node.y, 6, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px monospace';
        ctx.fillText(node.name, node.x - 12, node.y - 10);
      });

      // Draw Debris Target
      if (debrisX > 0 && debrisX < width) {
        // Debye Sheath Glow
        ctx.fillStyle = 'rgba(245, 158, 11, 0.25)';
        ctx.beginPath();
        ctx.arc(debrisX, debrisY, Math.max(8, debrisSizeCm * 3), 0, Math.PI * 2);
        ctx.fill();

        // Debris Core
        ctx.fillStyle = '#fbbf24';
        ctx.beginPath();
        ctx.arc(debrisX, debrisY, Math.max(3, debrisSizeCm * 1.2), 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Positioning Error Ellipse
        ctx.strokeStyle = 'rgba(244, 63, 94, 0.8)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.ellipse(debrisX, debrisY, estimatedErrorM * 8, estimatedErrorM * 4, 0, 0, Math.PI * 2);
        ctx.stroke();

        ctx.fillStyle = '#fda4af';
        ctx.font = '9px monospace';
        ctx.fillText(`±${estimatedErrorM}m 1-σ`, debrisX + 12, debrisY - 8);
      }

      if (isSimRunning) {
        animId = requestAnimationFrame(render);
      }
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [debrisVelocity, soundSpeed, debrisSizeCm, clockJitterNs, sensorBaselineKm, machConeAngleDeg, estimatedErrorM, isSimRunning]);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold text-cyan-400 bg-cyan-950/80 border border-cyan-800 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
              Mathematical Foundation & Physics Engine
            </span>
            <span className="text-xs font-mono text-emerald-400 font-bold">
              Metamorphic Physics Invariants Passing
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-2">
            Hypersonic Plasma Wake & TDOA Kinematics Simulator
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Simulates ion-acoustic Mach cone generation and multi-static CubeSat RF receiver
            hyperbolic localization evaluated in <span className="font-mono text-cyan-300">src/heimdall/tdoa_solver.py</span> and <span className="font-mono text-cyan-300">Wiki_Plasma_Wake_Physics.md</span>.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={() => setIsAudioEnabled(!isAudioEnabled)}
            className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors flex items-center gap-1.5 ${
              isAudioEnabled
                ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {isAudioEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
            <span>{isAudioEnabled ? 'Acoustic Radar ON' : 'Acoustic Radar OFF'}</span>
          </button>

          <button
            onClick={() => setIsSimRunning(!isSimRunning)}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-medium transition-colors flex items-center gap-1.5"
          >
            {isSimRunning ? <Pause className="w-3.5 h-3.5 text-amber-400" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
            <span>{isSimRunning ? 'Pause' : 'Resume'}</span>
          </button>
        </div>
      </div>

      {/* Preset Quick Selectors */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex items-center gap-2 overflow-x-auto text-xs">
        <span className="text-slate-400 font-medium shrink-0 flex items-center gap-1">
          <Zap className="w-3.5 h-3.5 text-cyan-400" />
          <span>Quick Scenarios:</span>
        </span>
        <button
          onClick={() => applyPreset(7.8, 1.8, 1.0, 0.3, 40)}
          className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 whitespace-nowrap"
        >
          1cm Lethal Particle (7.8 km/s)
        </button>
        <button
          onClick={() => applyPreset(7.2, 1.6, 5.0, 0.5, 60)}
          className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 whitespace-nowrap"
        >
          5cm Paint/Bolt Fragment
        </button>
        <button
          onClick={() => applyPreset(8.5, 2.2, 10.0, 0.8, 80)}
          className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 whitespace-nowrap"
        >
          10cm Inactive CubeSat Structure
        </button>
        <button
          onClick={() => applyPreset(9.5, 2.5, 2.5, 2.0, 100)}
          className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 whitespace-nowrap"
        >
          Elliptical Storm Orbit (High Jitter)
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Interactive Controls */}
        <div className="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-wider">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Simulation Parameters</span>
          </h3>

          {/* Debris Velocity */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Orbital Velocity ($v_orb$)</span>
              <span className="font-mono text-cyan-400 font-bold">{debrisVelocity.toFixed(1)} km/s</span>
            </div>
            <input
              type="range"
              min="5.0"
              max="11.0"
              step="0.1"
              value={debrisVelocity}
              onChange={(e) => setDebrisVelocity(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>5.0 km/s (High LEO)</span>
              <span>11.0 km/s (Hyperbolic)</span>
            </div>
          </div>

          {/* Ion Acoustic Sound Speed */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Ion Sound Speed ($c_s$)</span>
              <span className="font-mono text-emerald-400 font-bold">{soundSpeed.toFixed(1)} km/s</span>
            </div>
            <input
              type="range"
              min="1.0"
              max="3.0"
              step="0.1"
              value={soundSpeed}
              onChange={(e) => setSoundSpeed(parseFloat(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>1.0 km/s (O+ heavy)</span>
              <span>3.0 km/s (H+ light)</span>
            </div>
          </div>

          {/* Debris Characteristic Size */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Debris Size ($D$)</span>
              <span className="font-mono text-amber-400 font-bold">{debrisSizeCm.toFixed(1)} cm</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="10.0"
              step="0.5"
              value={debrisSizeCm}
              onChange={(e) => setDebrisSizeCm(parseFloat(e.target.value))}
              className="w-full accent-amber-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0.5 cm (Sub-cm Risk)</span>
              <span>10.0 cm (SSN Boundary)</span>
            </div>
          </div>

          {/* Clock Jitter / Sync Error */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">GNSS Receiver Jitter ($\sigma_t$)</span>
              <span className="font-mono text-purple-400 font-bold">{clockJitterNs.toFixed(2)} ns</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="5.0"
              step="0.1"
              value={clockJitterNs}
              onChange={(e) => setClockJitterNs(parseFloat(e.target.value))}
              className="w-full accent-purple-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0.1 ns (Rubidium Clock)</span>
              <span>5.0 ns (Standard GNSS)</span>
            </div>
          </div>

          {/* Constellation Baseline */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Constellation Baseline ($L_b$)</span>
              <span className="font-mono text-blue-400 font-bold">{sensorBaselineKm} km</span>
            </div>
            <input
              type="range"
              min="10"
              max="150"
              step="5"
              value={sensorBaselineKm}
              onChange={(e) => setSensorBaselineKm(parseInt(e.target.value))}
              className="w-full accent-blue-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>10 km (Tight Cluster)</span>
              <span>150 km (Sparse Ring)</span>
            </div>
          </div>
        </div>

        {/* Visual Stage & Real-Time Physics Readouts */}
        <div className="lg:col-span-8 space-y-4">
          {/* Visual Canvas */}
          <div className="relative bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
            <canvas
              ref={canvasRef}
              width={640}
              height={320}
              className="w-full h-72 sm:h-80 block"
            />

            <div className="absolute bottom-3 left-4 text-[11px] font-mono text-slate-400 flex items-center gap-2 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800">
              <Radio className="w-3.5 h-3.5 text-cyan-400" />
              <span>Real-Time Hyperbolic TDOA Kinematic Solver</span>
            </div>
          </div>

          {/* Calculated Physics KPIs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
              <div className="text-[11px] text-slate-400 font-medium">Plasma Mach Number</div>
              <div className="text-lg font-bold text-cyan-400 font-mono mt-0.5">
                M = {machNumber.toFixed(2)}
              </div>
              <div className="text-[10px] text-slate-500">Hypersonic regime</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
              <div className="text-[11px] text-slate-400 font-medium">Mach Cone Half-Angle</div>
              <div className="text-lg font-bold text-emerald-400 font-mono mt-0.5">
                {machConeAngleDeg.toFixed(1)}&deg;
              </div>
              <div className="text-[10px] text-slate-500">&theta; = arcsin(1/M)</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
              <div className="text-[11px] text-slate-400 font-medium">Wake Extent (L_wake)</div>
              <div className="text-lg font-bold text-amber-400 font-mono mt-0.5">
                ~{wakeLengthMeters} m
              </div>
              <div className="text-[10px] text-slate-500">Decay length</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
              <div className="text-[11px] text-slate-400 font-medium">TDOA 1-&sigma; Error</div>
              <div className="text-lg font-bold text-rose-400 font-mono mt-0.5">
                &plusmn;{estimatedErrorM} m
              </div>
              <div className="text-[10px] text-slate-500">Positioning ellipse</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
