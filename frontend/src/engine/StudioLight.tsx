import { useThree } from '@react-three/fiber'
import { useEffect } from 'react'
import { PMREMGenerator } from 'three'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'

/**
 * Soft, even studio lighting for the 3D models' real materials (paper, card, plastic, steel).
 * Built in the browser from a simple room, so nothing is downloaded. The models keep their own
 * colours in both themes; only the background around them changes.
 */
export function StudioLight({ intensity = 0.85 }: { intensity?: number }) {
  const gl = useThree((s) => s.gl)
  const scene = useThree((s) => s.scene)
  const invalidate = useThree((s) => s.invalidate)
  useEffect(() => {
    const pmrem = new PMREMGenerator(gl)
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
    // The scene is three.js's mutable root object: setting its environment is how lighting is applied.
    // eslint-disable-next-line react/immutability
    scene.environment = env
    scene.environmentIntensity = intensity
    invalidate()
    return () => {
      scene.environment = null
      env.dispose()
      pmrem.dispose()
    }
  }, [gl, scene, intensity, invalidate])
  return null
}
