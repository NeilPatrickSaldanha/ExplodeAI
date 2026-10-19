import { OrbitControls } from '@react-three/drei'
import { Canvas, useFrame } from '@react-three/fiber'
import { useMemo, useState } from 'react'
import { scenePalette } from '../../engine/colors'
import { hasWebGL, useThemeVersion } from '../../engine/hooks'
import { Part3D } from '../../engine/Part3D'
import type { PartSpec } from '../../engine/types'

/**
 * The selected part on its own, slowly opening and closing its internal
 * sub-explosion so the learner sees what it is made of. Drag to rotate.
 * Reduced motion: shown half-open and still.
 */
export function PartCloseup({ part, reducedMotion, label }: { part: PartSpec; reducedMotion: boolean; label: string }) {
  if (!hasWebGL()) return null
  return (
    <div className="closeup">
      <Canvas frameloop={reducedMotion ? 'demand' : 'always'} camera={{ position: [1.6, 1.5, 2.4], fov: 38 }} role="img" aria-label={label} dpr={[1, 2]}>
        <Scene part={part} reducedMotion={reducedMotion} />
      </Canvas>
    </div>
  )
}

function Scene({ part, reducedMotion }: { part: PartSpec; reducedMotion: boolean }) {
  const v = useThemeVersion()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const pal = useMemo(() => scenePalette(), [v])
  const [t, setT] = useState(0.5)
  useFrame(({ clock }) => {
    if (reducedMotion) return
    const next = 0.5 + 0.5 * Math.sin(clock.getElapsedTime() * 0.9)
    if (Math.abs(next - t) > 0.01) setT(next)
  })
  const solo: PartSpec = { ...part, position: [0, -part.size[1] / 2, 0], explode: [0, 0, 0] }
  return (
    <>
      <color attach="background" args={[pal.paper]} />
      <ambientLight intensity={0.6} />
      <directionalLight position={[3, 5, 3]} intensity={1.1} />
      <directionalLight position={[-3, 2, -2]} intensity={0.4} />
      <Part3D part={solo} at={solo.position} explode={t} selected={false} dimmed={false} palette={{ ...pal, edge: pal.accent }} onSelect={() => {}} />
      <OrbitControls makeDefault enablePan={false} enableZoom={false} />
    </>
  )
}
