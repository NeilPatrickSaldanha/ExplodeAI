import { expect, test, type Page } from '@playwright/test'

const LESSON = '/lessons/attention'

/** Screen positions of the first three part labels. */
const positions = (page: Page) =>
  page.evaluate(() =>
    [...document.querySelectorAll('.part-label')].slice(0, 3).map((e) => {
      const r = e.getBoundingClientRect()
      return [r.left, r.top]
    }),
  )

async function drag(page: Page, dx: number, dy: number) {
  const box = (await page.locator('.scene canvas').boundingBox())!
  const x = box.x + box.width * 0.5
  const y = box.y + box.height * 0.6
  await page.mouse.move(x, y)
  await page.mouse.down()
  await page.mouse.move(x + dx, y + dy, { steps: 12 })
  await page.mouse.up()
  await page.waitForTimeout(900) // let the damping settle
}

const settle = async (page: Page) => {
  await page.waitForTimeout(1800) // the entrance animation and first stage selection
}

test('Move (hand) mode: dragging slides the whole diagram, and it stays where you put it', async ({ page }) => {
  await page.goto(LESSON)
  await settle(page)
  const move = page.getByRole('button', { name: /Move/ })
  await expect(move).toHaveAttribute('aria-pressed', 'false')
  await move.click()
  await expect(move).toHaveAttribute('aria-pressed', 'true')
  await expect(page.locator('.scene')).toHaveAttribute('data-pan', 'true')
  const before = await positions(page)
  await drag(page, 140, 30)
  const after = await positions(page)
  const dx = after.map((p, i) => p[0] - before[i][0])
  const dy = after.map((p, i) => p[1] - before[i][1])
  // Every part moved the same way, by roughly the same amount: a slide, not a rotation.
  for (const d of dx) expect(d).toBeGreaterThan(60)
  expect(Math.max(...dx) - Math.min(...dx)).toBeLessThan(0.35 * Math.max(...dx))
  for (const d of dy) expect(d).toBeGreaterThan(5)
  // The camera does not drift back towards the selected stage afterwards (a little damping is fine).
  await page.waitForTimeout(1500)
  const later = await positions(page)
  later.forEach((p, i) => {
    expect(Math.abs(p[0] - after[i][0])).toBeLessThan(40)
    expect(p[0] - before[i][0]).toBeGreaterThan(60)
  })
  // Reset camera brings everything back.
  await page.getByRole('button', { name: 'Reset camera' }).click()
  await page.waitForTimeout(900)
  const reset = await positions(page)
  reset.forEach((p, i) => {
    expect(Math.abs(p[0] - before[i][0])).toBeLessThan(40)
  })
})

test('with Move off, dragging still rotates the diagram (parts shift by different amounts)', async ({ page }) => {
  await page.goto(LESSON)
  await settle(page)
  const before = await positions(page)
  await drag(page, 140, 0)
  const after = await positions(page)
  const dx = after.map((p, i) => p[0] - before[i][0])
  expect(Math.max(...dx) - Math.min(...dx)).toBeGreaterThan(0.35 * Math.max(...dx.map(Math.abs)))
})

test('Move can be switched off again, and is unavailable in the 2D view', async ({ page }) => {
  await page.goto(LESSON)
  const move = page.getByRole('button', { name: /Move/ })
  await move.click()
  await move.click()
  await expect(move).toHaveAttribute('aria-pressed', 'false')
  await page.getByRole('button', { name: '3D', exact: true }).click()
  await expect(move).toBeDisabled()
})
