import { PerspectiveCamera, Vector3 } from 'three'
import type { Vec3 } from './types'

export const FOV = 38
/** Camera direction from the target: front three-quarter view, fairly high so rows separate. */
export const VIEW_DIR = new Vector3(0.06, 0.78, 0.62).normalize()
/** Portrait screens: orbit 90° and look more steeply down so the long x-axis runs vertically. */
export const VIEW_DIR_PORTRAIT = new Vector3(0.5, 0.86, 0.02).normalize()

export const viewDirFor = (aspect: number) => (aspect < 0.85 ? VIEW_DIR_PORTRAIT : VIEW_DIR)

/**
 * Smallest camera distance (along VIEW_DIR) at which every point projects inside
 * the central `margin` of the viewport. Binary search with a scratch camera.
 */
export function fitDistance(
  points: Vec3[],
  center: Vec3,
  aspect: number,
  margin = 0.76,
  dir = viewDirFor(aspect),
  marginY = margin,
): number {
  const cam = new PerspectiveCamera(FOV, aspect, 0.1, 500)
  const c = new Vector3(...center)
  const v = new Vector3()
  const fits = (d: number) => {
    cam.position.copy(c).addScaledVector(dir, d)
    cam.lookAt(c)
    cam.updateMatrixWorld()
    return points.every((p) => {
      v.set(p[0], p[1], p[2]).project(cam)
      return Math.abs(v.x) <= margin && Math.abs(v.y) <= marginY && v.z < 1
    })
  }
  let lo = 1
  let hi = 200
  for (let i = 0; i < 30; i++) {
    const mid = (lo + hi) / 2
    if (fits(mid)) hi = mid
    else lo = mid
  }
  return hi
}

export interface FitOptions {
  /** Half-width of the usable area in NDC (1 = the full canvas width). */
  marginX: number
  /** Half-height of the usable area in NDC. */
  marginY: number
  /** Where the usable area is centred vertically in NDC (positive = above the middle). */
  centerY?: number
  dir?: Vector3
}

/**
 * Frame points so they fill the usable area and sit in its middle. The distance search alone
 * keeps points inside, but it aims at the average position of the parts, which is not the middle
 * of what is drawn: a stretched, tilted layout ends up off to one side. So: fit, measure the
 * projected box, slide the target so the box is centred, and fit again.
 */
export interface FitPoint {
  at: Vec3
  /** Extra room to the left and right of the point, in NDC (a label centred on it). */
  padX?: number
  /** Extra room above the point, in NDC (a label that hangs above its anchor). */
  padTop?: number
}

export function fitView(rawPoints: (Vec3 | FitPoint)[], center: Vec3, aspect: number, opts: FitOptions): { distance: number; target: Vec3 } {
  const points: FitPoint[] = rawPoints.map((p) => (Array.isArray(p) ? { at: p as Vec3 } : (p as FitPoint)))
  const dir = opts.dir ?? viewDirFor(aspect)
  const centerY = opts.centerY ?? 0
  const cam = new PerspectiveCamera(FOV, aspect, 0.1, 500)
  const target = new Vector3(...center)
  const v = new Vector3()
  const place = (d: number) => {
    cam.position.copy(target).addScaledVector(dir, d)
    cam.lookAt(target)
    cam.updateMatrixWorld()
  }
  const fits = (d: number) => {
    place(d)
    return points.every((p) => {
      v.set(p.at[0], p.at[1], p.at[2]).project(cam)
      const px = p.padX ?? 0
      const pt = p.padTop ?? 0
      return (
        v.x - px >= -opts.marginX &&
        v.x + px <= opts.marginX &&
        v.y - centerY >= -opts.marginY &&
        v.y + pt - centerY <= opts.marginY &&
        v.z < 1
      )
    })
  }
  const search = () => {
    let lo = 1
    let hi = 200
    for (let i = 0; i < 30; i++) {
      const mid = (lo + hi) / 2
      if (fits(mid)) hi = mid
      else lo = mid
    }
    return hi
  }
  let d = search()
  for (let i = 0; i < 4; i++) {
    place(d)
    let minX = Infinity
    let maxX = -Infinity
    let minY = Infinity
    let maxY = -Infinity
    for (const p of points) {
      v.set(p.at[0], p.at[1], p.at[2]).project(cam)
      minX = Math.min(minX, v.x - (p.padX ?? 0))
      maxX = Math.max(maxX, v.x + (p.padX ?? 0))
      minY = Math.min(minY, v.y)
      maxY = Math.max(maxY, v.y + (p.padTop ?? 0))
    }
    const dx = (minX + maxX) / 2
    const dy = (minY + maxY) / 2 - centerY
    if (Math.abs(dx) < 0.003 && Math.abs(dy) < 0.003) break
    const halfH = d * Math.tan((FOV * Math.PI) / 360)
    const right = new Vector3().setFromMatrixColumn(cam.matrixWorld, 0)
    const up = new Vector3().setFromMatrixColumn(cam.matrixWorld, 1)
    target.addScaledVector(right, dx * halfH * aspect).addScaledVector(up, dy * halfH)
    d = search()
  }
  return { distance: d, target: [target.x, target.y, target.z] }
}
