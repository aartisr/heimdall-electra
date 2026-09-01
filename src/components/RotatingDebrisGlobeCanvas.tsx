import React, { useRef, useEffect, useState, useCallback } from 'react';
import {
  RotateCw,
  Play,
  Pause,
  ZoomIn,
  ZoomOut,
  Layers,
  Sparkles,
  Info,
  Maximize2,
  RefreshCw,
} from 'lucide-react';

interface Particle {
  x: number;
  y: number;
  z: number;
  radius: number;
  inclination: number; // orbital inclination in radians
  raan: number;        // Right Ascension of Ascending Node in radians
  trueAnomaly: number; // orbital position angle
  speed: number;       // angular velocity
  type: 'tracked' | 'near_detectable' | 'sub_cm' | 'fragmentation';
  size: number;
  color: string;
  clusterId?: number;
}

export const RotatingDebrisGlobeCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Toggles for layers matching authentic screenshot
  const [showTracked, setShowTracked] = useState<boolean>(true);
  const [showNearDetectable, setShowNearDetectable] = useState<boolean>(true);
  const [showSubCm, setShowSubCm] = useState<boolean>(true);
  const [showFragmentation, setShowFragmentation] = useState<boolean>(true);

  // Simulation controls
  const [isRotating, setIsRotating] = useState<boolean>(true);
  const [zoom, setZoom] = useState<number>(1.0);
  const [rotationSpeed, setRotationSpeed] = useState<number>(1.0);

  // Mouse drag state
  const isDraggingRef = useRef<boolean>(false);
  const previousMousePositionRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const rotationAnglesRef = useRef<{ rotX: number; rotY: number }>({ rotX: 0.25, rotY: 0.0 });

  // Particles
  const particlesRef = useRef<Particle[]>([]);

  const initParticles = useCallback(() => {
    const particles: Particle[] = [];
    const earthRadius = 110;

    // 1. Sub-cm Debris (HEIMDALL domain, ~2400 particles visually representing 2.4B statistical cloud)
    for (let i = 0; i < 2400; i++) {
      const r = earthRadius + 18 + Math.pow(Math.random(), 1.6) * 80;
      const inc = (Math.random() * 0.95 + 0.35) * (Math.random() > 0.3 ? 1 : -1);
      const raan = Math.random() * Math.PI * 2;
      const trueAnomaly = Math.random() * Math.PI * 2;
      const speed = (0.003 + Math.random() * 0.004) * (Math.random() > 0.1 ? 1 : -1);

      particles.push({
        x: 0,
        y: 0,
        z: 0,
        radius: r,
        inclination: inc,
        raan,
        trueAnomaly,
        speed,
        type: 'sub_cm',
        size: 0.8 + Math.random() * 0.8,
        color: '#f97316', // Orange / copper
      });
    }

    // 2. Near-detectable (1-10cm, ~750 particles)
    for (let i = 0; i < 750; i++) {
      const r = earthRadius + 22 + Math.random() * 65;
      const inc = (Math.random() * 1.1 + 0.2) * (Math.random() > 0.5 ? 1 : -1);
      const raan = Math.random() * Math.PI * 2;
      const trueAnomaly = Math.random() * Math.PI * 2;
      const speed = 0.0035 + Math.random() * 0.003;

      particles.push({
        x: 0,
        y: 0,
        z: 0,
        radius: r,
        inclination: inc,
        raan,
        trueAnomaly,
        speed,
        type: 'near_detectable',
        size: 1.2 + Math.random() * 0.8,
        color: '#eab308', // Amber / Gold
      });
    }

    // 3. Tracked (>10cm macro cataloged, ~450 particles)
    for (let i = 0; i < 450; i++) {
      const r = earthRadius + 25 + Math.random() * 85;
      const inc = (Math.random() * 1.4 + 0.1) * (Math.random() > 0.5 ? 1 : -1);
      const raan = Math.random() * Math.PI * 2;
      const trueAnomaly = Math.random() * Math.PI * 2;
      const speed = 0.003 + Math.random() * 0.0025;

      particles.push({
        x: 0,
        y: 0,
        z: 0,
        radius: r,
        inclination: inc,
        raan,
        trueAnomaly,
        speed,
        type: 'tracked',
        size: 1.6 + Math.random() * 0.8,
        color: '#94a3b8', // Slate / Gray-white
      });
    }

    // 4. Fragmentation Clouds (Dense concentrated clusters, Fengyun-1C, Iridium/Cosmos, Cosmos-1408)
    const clusters = [
      { r: earthRadius + 60, inc: 1.72, raan: 0.8, count: 280, color: '#c084fc' }, // Fengyun-1C polar
      { r: earthRadius + 52, inc: 1.5, raan: 3.2, count: 220, color: '#d8b4fe' },  // Iridium-33
      { r: earthRadius + 53, inc: 1.3, raan: 3.6, count: 180, color: '#c084fc' },  // Cosmos-2251
      { r: earthRadius + 38, inc: 1.44, raan: 5.1, count: 200, color: '#e879f9' }, // Cosmos-1408 ASAT
      { r: earthRadius + 42, inc: 0.92, raan: 1.9, count: 140, color: '#a855f7' }, // Resurs-P fragment
      { r: earthRadius + 75, inc: 1.15, raan: 4.4, count: 130, color: '#c084fc' }, // Upper Stage Breakup
    ];

    clusters.forEach((cluster, cIdx) => {
      for (let i = 0; i < cluster.count; i++) {
        const spreadR = cluster.r + (Math.random() - 0.5) * 8;
        const spreadInc = cluster.inc + (Math.random() - 0.5) * 0.08;
        const spreadRaan = cluster.raan + (Math.random() - 0.5) * 0.15;
        const trueAnomaly = Math.random() * 0.5 + cIdx * 1.0;
        const speed = 0.0038 + (Math.random() - 0.5) * 0.0004;

        particles.push({
          x: 0,
          y: 0,
          z: 0,
          radius: spreadR,
          inclination: spreadInc,
          raan: spreadRaan,
          trueAnomaly,
          speed,
          type: 'fragmentation',
          size: 1.5 + Math.random() * 1.0,
          color: cluster.color,
          clusterId: cIdx,
        });
      }
    });

    particlesRef.current = particles;
  }, []);

  useEffect(() => {
    initParticles();
  }, [initParticles]);

  // Main 3D Canvas Rendering Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;

    const render = () => {
      const width = canvas.clientWidth || 800;
      const height = canvas.clientHeight || 500;
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }

      ctx.clearRect(0, 0, width, height);

      const centerX = width / 2;
      const centerY = height / 2;
      const earthRadius = 110 * zoom;

      // Update rotation
      if (isRotating && !isDraggingRef.current) {
        rotationAnglesRef.current.rotY += 0.004 * rotationSpeed;
      }

      const rotX = rotationAnglesRef.current.rotX;
      const rotY = rotationAnglesRef.current.rotY;

      const cosX = Math.cos(rotX);
      const sinX = Math.sin(rotX);
      const cosY = Math.cos(rotY);
      const sinY = Math.sin(rotY);

      // Compute particle 3D coordinates & project to 2D
      const projectedParticles: {
        px: number;
        py: number;
        pz: number;
        p: Particle;
        alpha: number;
      }[] = [];

      for (const p of particlesRef.current) {
        if (p.type === 'tracked' && !showTracked) continue;
        if (p.type === 'near_detectable' && !showNearDetectable) continue;
        if (p.type === 'sub_cm' && !showSubCm) continue;
        if (p.type === 'fragmentation' && !showFragmentation) continue;

        if (isRotating) {
          p.trueAnomaly += p.speed * rotationSpeed;
        }

        const orbX = p.radius * Math.cos(p.trueAnomaly);
        const orbY = p.radius * Math.sin(p.trueAnomaly);

        const incCos = Math.cos(p.inclination);
        const incSin = Math.sin(p.inclination);
        const raanCos = Math.cos(p.raan);
        const raanSin = Math.sin(p.raan);

        const ex = (raanCos * orbX - raanSin * orbY * incCos) * zoom;
        const ey = (orbY * incSin) * zoom;
        const ez = (raanSin * orbX + raanCos * orbY * incCos) * zoom;

        // 1. Around Y-axis
        const x1 = ex * cosY - ez * sinY;
        const y1 = ey;
        const z1 = ex * sinY + ez * cosY;

        // 2. Around X-axis
        const x2 = x1;
        const y2 = y1 * cosX - z1 * sinX;
        const z2 = y1 * sinX + z1 * cosX;

        const cameraDist = 600;
        const scale = cameraDist / (cameraDist - z2);
        const px = centerX + x2 * scale;
        const py = centerY + y2 * scale;

        const depthNorm = (z2 + 250) / 500;
        const alpha = Math.max(0.12, Math.min(1.0, depthNorm * 0.9 + 0.15));

        projectedParticles.push({
          px,
          py,
          pz: z2,
          p,
          alpha,
        });
      }

      projectedParticles.sort((a, b) => a.pz - b.pz);

      // 1. Radial Background Glow
      const bgGlow = ctx.createRadialGradient(
        centerX,
        centerY,
        earthRadius * 0.6,
        centerX,
        centerY,
        earthRadius * 2.4
      );
      bgGlow.addColorStop(0, 'rgba(14, 116, 144, 0.22)');
      bgGlow.addColorStop(0.5, 'rgba(6, 78, 119, 0.08)');
      bgGlow.addColorStop(1, 'rgba(2, 6, 23, 0)');
      ctx.fillStyle = bgGlow;
      ctx.fillRect(0, 0, width, height);

      const backParticles = projectedParticles.filter((pt) => pt.pz < 0);
      const frontParticles = projectedParticles.filter((pt) => pt.pz >= 0);

      // Draw BACK Particles (behind Earth)
      for (const pt of backParticles) {
        ctx.fillStyle = pt.p.color;
        ctx.globalAlpha = pt.alpha * 0.45;
        ctx.beginPath();
        ctx.arc(pt.px, pt.py, pt.p.size * (pt.p.type === 'fragmentation' ? 1.4 : 0.9), 0, Math.PI * 2);
        ctx.fill();
      }

      // 2. Draw 3D EARTH GLOBE in Center
      ctx.save();
      ctx.globalAlpha = 1.0;

      const earthGradient = ctx.createRadialGradient(
        centerX - earthRadius * 0.35,
        centerY - earthRadius * 0.35,
        earthRadius * 0.1,
        centerX,
        centerY,
        earthRadius
      );
      earthGradient.addColorStop(0, '#155e75');   // Cyan specular highlight
      earthGradient.addColorStop(0.4, '#0e3b54'); // Deep ocean teal
      earthGradient.addColorStop(0.85, '#082538'); // Dark rim ocean
      earthGradient.addColorStop(1, '#03121d');   // Terminator limb

      ctx.beginPath();
      ctx.arc(centerX, centerY, earthRadius, 0, Math.PI * 2);
      ctx.fillStyle = earthGradient;
      ctx.fill();

      // Atmospheric limb glow
      ctx.lineWidth = 2.5;
      const atmoGlow = ctx.createRadialGradient(
        centerX,
        centerY,
        earthRadius * 0.92,
        centerX,
        centerY,
        earthRadius * 1.08
      );
      atmoGlow.addColorStop(0, 'rgba(56, 189, 248, 0.4)');
      atmoGlow.addColorStop(0.6, 'rgba(14, 165, 233, 0.25)');
      atmoGlow.addColorStop(1, 'rgba(2, 132, 199, 0)');
      ctx.strokeStyle = atmoGlow;
      ctx.stroke();

      // Latitude / Longitude 3D Graticule Grid on Globe
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.14)';
      ctx.lineWidth = 1;

      for (let lat = -60; lat <= 60; lat += 30) {
        const latRad = (lat * Math.PI) / 180;
        const rLat = earthRadius * Math.cos(latRad);
        const yLat = earthRadius * Math.sin(latRad);

        ctx.beginPath();
        for (let lon = 0; lon <= 360; lon += 10) {
          const lonRad = (lon * Math.PI) / 180 + rotY;
          const gx = rLat * Math.sin(lonRad);
          const gy = yLat;
          const gz = rLat * Math.cos(lonRad);

          const gy2 = gy * cosX - gz * sinX;
          const gz2 = gy * sinX + gz * cosX;

          if (gz2 >= -10) {
            const sx = centerX + gx;
            const sy = centerY + gy2;
            if (lon === 0) ctx.moveTo(sx, sy);
            else ctx.lineTo(sx, sy);
          }
        }
        ctx.stroke();
      }

      for (let lon = 0; lon < 180; lon += 45) {
        ctx.beginPath();
        for (let lat = -90; lat <= 90; lat += 6) {
          const latRad = (lat * Math.PI) / 180;
          const lonRad = (lon * Math.PI) / 180 + rotY;

          const gx = earthRadius * Math.cos(latRad) * Math.sin(lonRad);
          const gy = earthRadius * Math.sin(latRad);
          const gz = earthRadius * Math.cos(latRad) * Math.cos(lonRad);

          const gy2 = gy * cosX - gz * sinX;
          const gz2 = gy * sinX + gz * cosX;

          if (gz2 >= -10) {
            const sx = centerX + gx;
            const sy = centerY + gy2;
            if (lat === -90) ctx.moveTo(sx, sy);
            else ctx.lineTo(sx, sy);
          }
        }
        ctx.stroke();
      }

      ctx.restore();

      // Draw FRONT Particles
      for (const pt of frontParticles) {
        ctx.fillStyle = pt.p.color;
        ctx.globalAlpha = Math.min(1.0, pt.alpha * 1.1);

        if (pt.p.type === 'fragmentation') {
          ctx.shadowColor = '#d946ef';
          ctx.shadowBlur = 4;
          ctx.beginPath();
          ctx.arc(pt.px, pt.py, pt.p.size * 1.3, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
        } else {
          ctx.beginPath();
          ctx.arc(pt.px, pt.py, pt.p.size, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      ctx.globalAlpha = 1.0;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [
    isRotating,
    zoom,
    rotationSpeed,
    showTracked,
    showNearDetectable,
    showSubCm,
    showFragmentation,
  ]);

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    isDraggingRef.current = true;
    previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDraggingRef.current) return;
    const deltaX = e.clientX - previousMousePositionRef.current.x;
    const deltaY = e.clientY - previousMousePositionRef.current.y;

    rotationAnglesRef.current.rotY += deltaX * 0.008;
    rotationAnglesRef.current.rotX = Math.max(
      -1.2,
      Math.min(1.2, rotationAnglesRef.current.rotX + deltaY * 0.008)
    );

    previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  return (
    <div className="bg-[#0b1320] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xl relative">
      {/* Title & Authentic Sub-stats matching screenshot */}
      <div className="space-y-3">
        <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
          Orbital Debris Cloud Distribution
        </h3>

        {/* Counter Badges: 133,272 tracked | 2.4B sub-cm | 6 fragmentation events */}
        <div className="flex items-center gap-4 sm:gap-6 flex-wrap text-xs sm:text-sm font-mono">
          <div className="flex items-center gap-1.5">
            <span className="text-white font-black text-base sm:text-lg">133,272</span>
            <span className="text-slate-400 font-sans">tracked</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-[#f97316] font-black text-base sm:text-lg">2.4B</span>
            <span className="text-slate-400 font-sans">sub-cm (estimated)</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-[#c084fc] font-black text-base sm:text-lg">6</span>
            <span className="text-slate-400 font-sans">fragmentation events</span>
          </div>
        </div>
      </div>

      {/* 3D Interactive Rotating Canvas Container */}
      <div className="relative w-full h-[400px] sm:h-[480px] md:h-[540px] bg-[#070d18] rounded-2xl overflow-hidden border border-slate-800/80 shadow-inner group">
        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className="w-full h-full cursor-grab active:cursor-grabbing block"
        />

        {/* Interactive Overlay Controls */}
        <div className="absolute top-4 right-4 flex items-center gap-2 bg-slate-950/80 backdrop-blur-md border border-slate-800 p-1.5 rounded-xl text-xs z-10 shadow-lg">
          <button
            onClick={() => setIsRotating(!isRotating)}
            title={isRotating ? 'Pause Rotation' : 'Resume Rotation'}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            {isRotating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 text-cyan-400" />}
          </button>

          <button
            onClick={() => setZoom((z) => Math.min(1.6, z + 0.15))}
            title="Zoom In"
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <ZoomIn className="w-4 h-4" />
          </button>

          <button
            onClick={() => setZoom((z) => Math.max(0.65, z - 0.15))}
            title="Zoom Out"
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <ZoomOut className="w-4 h-4" />
          </button>

          <button
            onClick={() => {
              setZoom(1.0);
              rotationAnglesRef.current = { rotX: 0.25, rotY: 0.0 };
            }}
            title="Reset View"
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Drag Hint */}
        <div className="absolute bottom-3 left-4 text-[11px] text-slate-500 font-mono pointer-events-none bg-slate-950/60 px-2 py-0.5 rounded">
          Click &amp; drag globe to rotate 3D view
        </div>
      </div>

      {/* Authentic Interactive Filter Legends matching Screenshot */}
      <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap">
        {/* Tracked (> 10 cm) */}
        <button
          onClick={() => setShowTracked(!showTracked)}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium border transition-all ${
            showTracked
              ? 'bg-slate-900/90 text-slate-300 border-slate-700 shadow-sm'
              : 'bg-slate-950/40 text-slate-600 border-slate-900 opacity-60'
          }`}
        >
          <span className={`w-2.5 h-2.5 rounded-full bg-slate-400 ${!showTracked && 'opacity-30'}`} />
          <span>Tracked (&gt; 10 cm)</span>
        </button>

        {/* Near-detectable (1-10 cm) */}
        <button
          onClick={() => setShowNearDetectable(!showNearDetectable)}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium border transition-all ${
            showNearDetectable
              ? 'bg-slate-900/90 text-yellow-300 border-yellow-800/60 shadow-sm'
              : 'bg-slate-950/40 text-slate-600 border-slate-900 opacity-60'
          }`}
        >
          <span className={`w-2.5 h-2.5 rounded-full bg-yellow-400 ${!showNearDetectable && 'opacity-30'}`} />
          <span>Near-detectable (1–10 cm)</span>
        </button>

        {/* Sub-cm (HEIMDALL) */}
        <button
          onClick={() => setShowSubCm(!showSubCm)}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold border transition-all ${
            showSubCm
              ? 'bg-[#f97316]/15 text-[#f97316] border-[#f97316] shadow-sm shadow-orange-500/10'
              : 'bg-slate-950/40 text-slate-600 border-slate-900 opacity-60'
          }`}
        >
          <span className={`w-2.5 h-2.5 rounded-full bg-[#f97316] ${!showSubCm && 'opacity-30'}`} />
          <span>Sub-cm (HEIMDALL)</span>
        </button>

        {/* Fragmentation clouds */}
        <button
          onClick={() => setShowFragmentation(!showFragmentation)}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold border transition-all ${
            showFragmentation
              ? 'bg-[#c084fc]/15 text-[#c084fc] border-[#c084fc] shadow-sm shadow-purple-500/10'
              : 'bg-slate-950/40 text-slate-600 border-slate-900 opacity-60'
          }`}
        >
          <span className={`w-2.5 h-2.5 rounded-full bg-[#c084fc] ${!showFragmentation && 'opacity-30'}`} />
          <span>Fragmentation clouds</span>
        </button>
      </div>

      {/* Authentic Evidence Class Footer from GitHub Repository */}
      <div className="pt-2 text-xs text-slate-400 leading-relaxed border-t border-slate-800/80">
        <p>
          <span className="text-slate-200 font-bold">Evidence class: synthetic</span> — Synthetic power-law extrapolation. Sub-cm counts are statistical estimates with &plusmn;50% uncertainty based on published size-distribution indices. No direct sub-cm detection is claimed. Tracked counts are approximations of publicly available catalog distributions, not live TLE data.
        </p>
      </div>
    </div>
  );
};
