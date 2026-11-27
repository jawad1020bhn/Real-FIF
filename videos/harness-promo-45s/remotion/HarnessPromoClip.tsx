import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { useGsapTimeline } from '@remotion/gsap';
import * as THREE from 'three';

export const HarnessPromoClip: React.FC = () => {
  const frame = useCurrentFrame();
  const rotation = interpolate(frame, [0, 120], [0, Math.PI * 2], { extrapolateRight: 'clamp' });
  const scope = useGsapTimeline<HTMLDivElement>(({ timeline, selector }) => {
    timeline.fromTo(
      selector('.r-card'),
      { opacity: 0, y: 48, scale: 0.94 },
      { opacity: 1, y: 0, scale: 1, duration: 0.8, stagger: 0.14, ease: 'power3.out' },
      0.05,
    );
    timeline.fromTo(
      selector('.r-bar'),
      { scaleX: 0 },
      { scaleX: 1, duration: 1.3, ease: 'none' },
      0.2,
    );
  }, { dependencies: [] });

  return (
    <AbsoluteFill style={{ background: '#07070A', color: '#F5F5F7', fontFamily: 'sans-serif' }}>
      <ThreeCanvas
        width={1080}
        height={1920}
        camera={{ position: [0, 0, 6], fov: 45 }}
        gl={{ alpha: true, antialias: true }}
        style={{ position: 'absolute', inset: 0 }}
      >
        <ambientLight intensity={0.8} />
        <pointLight position={[4, 4, 7]} intensity={2.4} color="#F3D489" />
        <mesh rotation={[rotation * 0.6, rotation, rotation * 0.2]}>
          <icosahedronGeometry args={[1.45, 1]} />
          <meshBasicMaterial color="#D9A84E" wireframe />
        </mesh>
        <mesh rotation={[-rotation * 0.4, rotation * 0.8, 0]} scale={1.7}>
          <torusGeometry args={[1.6, 0.018, 8, 96]} />
          <meshBasicMaterial color="#F3D489" wireframe />
        </mesh>
      </ThreeCanvas>
      <div ref={scope} style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
        <div className="r-label" style={{ position: 'absolute', left: 120, top: 340, fontSize: 34, letterSpacing: '0.22em', color: '#D9A84E', fontWeight: 700 }}>
          REMOTION · THREE · GSAP
        </div>
        <div className="r-headline" style={{ position: 'absolute', left: 120, right: 120, top: 410, fontSize: 92, lineHeight: 1.02, fontWeight: 800, color: '#FFFFFF', textShadow: '0 8px 40px rgba(0,0,0,.9)' }}>
          FRAME-LOCKED<br/>MOTION
        </div>
        <div className="r-card" style={{ position: 'absolute', left: 120, top: 760, width: 320, padding: '26px 28px', borderRadius: 24, background: 'rgba(16,18,24,.82)', border: '1px solid rgba(217,168,78,.5)', fontSize: 30, color: '#F1E8D5' }}>
          useCurrentFrame
        </div>
        <div className="r-card" style={{ position: 'absolute', left: 470, top: 760, width: 320, padding: '26px 28px', borderRadius: 24, background: 'rgba(16,18,24,.82)', border: '1px solid rgba(217,168,78,.5)', fontSize: 30, color: '#F1E8D5' }}>
          useGsapTimeline
        </div>
        <div className="r-card" style={{ position: 'absolute', left: 120, top: 890, width: 670, padding: '26px 28px', borderRadius: 24, background: 'rgba(16,18,24,.82)', border: '1px solid rgba(217,168,78,.5)', fontSize: 30, color: '#F1E8D5' }}>
          ThreeCanvas + @remotion/three
        </div>
        <div style={{ position: 'absolute', left: 120, right: 120, bottom: 720, height: 8, background: 'rgba(255,255,255,.14)' }}>
          <div className="r-bar" style={{ height: '100%', width: '100%', background: 'linear-gradient(90deg,#D9A84E,#F3D489)', transformOrigin: 'left center' }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
