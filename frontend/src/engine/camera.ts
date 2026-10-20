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
