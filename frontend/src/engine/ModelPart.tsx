import { useGLTF } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import { Component, Suspense, useEffect, useLayoutEffect, useMemo, type ReactNode } from 'react'
import { Box3, Color, Vector3, type Material, type Mesh, type MeshStandardMaterial, type Object3D } from 'three'

/**
 * A stage drawn from a 3D model (a .glb file made in Blender) instead of a generic shape.
 * Nodes that carry `extras.explode = [dx, dy, dz]` move by that much at full internal explosion,
 * so a model can open up the way the generic shapes do. While the file loads, or if it fails,
 * the generic shape is shown instead.
 */
export function ModelPart({ url, width, t, opacity, highlight, fallback }: { url: string; width: number; t: number; opacity: number; highlight?: string; fallback: ReactNode }) {
  return (
    <ModelBoundary fallback={fallback}>
      <Suspense fallback={fallback}>
        <ModelMeshes url={url} width={width} t={t} opacity={opacity} highlight={highlight} />
      </Suspense>
    </ModelBoundary>
  )
}

interface Mover {
  obj: Object3D
  base: Vector3
  offset: Vector3
}

function ModelMeshes({ url, width, t, opacity, highlight }: { url: string; width: number; t: number; opacity: number; highlight?: string }) {
  // The models are Draco-compressed. The decoder is served from this site (public/draco), never a CDN.
  const { scene } = useGLTF(url, '/draco/')
  const invalidate = useThree((s) => s.invalidate)
  const { root, movers, materials } = useMemo(() => {
    const root = scene.clone(true)
    // Scale the model so its width matches the stage's size in the lesson data, which also places its label.
    const box = new Box3().setFromObject(root)
    const w = box.max.x - box.min.x
    if (w > 0) root.scale.setScalar(width / w)
    const movers: Mover[] = []
    const materials: MeshStandardMaterial[] = []
    root.traverse((o) => {
      const e = o.userData?.explode
      if (Array.isArray(e) && e.length === 3) movers.push({ obj: o, base: o.position.clone(), offset: new Vector3(e[0], e[1], e[2]) })
      const mesh = o as Mesh
      if (mesh.isMesh) {
        // Each part gets its own materials, so dimming or highlighting one stage leaves the others alone.
        const own = (mesh.material as Material).clone() as MeshStandardMaterial
        // Remember how see-through the model made this material (glass), so dimming never makes it solid.
        own.userData.baseOpacity = own.opacity
        mesh.material = own
        materials.push(own)
      }
    })
    return { root, movers, materials }
  }, [scene, width])

  useLayoutEffect(() => {
    for (const m of movers) m.obj.position.copy(m.base).addScaledVector(m.offset, t)
    invalidate()
  }, [movers, t, invalidate])

  useLayoutEffect(() => {
    const glow = highlight ? new Color(highlight) : null
    for (const m of materials) {
      const base = (m.userData.baseOpacity as number | undefined) ?? 1
      // three.js materials are mutable objects owned by this component; changing them is the intent.
      // eslint-disable-next-line react/immutability
      m.opacity = base * opacity
      m.transparent = m.opacity < 1
      m.depthWrite = !m.transparent
      if ('emissive' in m && m.emissive) {
        m.emissive.copy(glow ?? new Color(0, 0, 0))
        m.emissiveIntensity = glow ? 0.16 : 0
      }
      m.needsUpdate = true
    }
    invalidate()
  }, [materials, opacity, highlight, invalidate])

  useEffect(() => () => materials.forEach((m) => m.dispose()), [materials])

  return <primitive object={root} />
}

class ModelBoundary extends Component<{ fallback: ReactNode; children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  render() {
    return this.state.failed ? this.props.fallback : this.props.children
  }
}
