import { expect, test, type Page } from '@playwright/test'

// A first-time visitor: nothing remembered.
test.use({ storageState: { cookies: [], origins: [] } })

const card = (page: Page) => page.getByRole('dialog', { name: /./ })
const next = (page: Page) => page.locator('.tut__next')

test('first visit offers the tutorial once; skipping remembers it', async ({ page }) => {
  await page.goto('/lessons/embeddings')
  await expect(card(page)).toBeVisible()
  await expect(page.locator('.tut__title')).toHaveText(/welcome to explodeai/i)
  await page.getByRole('button', { name: 'Skip', exact: true }).click()
  await expect(card(page)).toBeHidden()
  await page.reload()
  await page.waitForTimeout(2200)
  await expect(card(page)).toBeHidden()
  // Replay on demand, and Escape skips again.
  await page.getByRole('button', { name: 'How to use' }).click()
  await expect(card(page)).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(card(page)).toBeHidden()
  await expect(page.getByRole('button', { name: 'How to use' })).toBeFocused()
})

test('walkthrough: spotlights controls, asks for real actions, and finishes', async ({ page }) => {
  await page.goto('/lessons/embeddings')
  await expect(card(page)).toBeVisible()
  await next(page).click() // Start
  // Rotate: the task completes only after a real drag on the model.
  await expect(page.locator('.tut__title')).toHaveText(/turn the machine/i)
  await expect(page.locator('.tut__ring')).toBeVisible()
  await expect(page.locator('.tut__task')).toContainText('Try it')
  const box = (await page.locator('.cine__frame').boundingBox())!
  await page.mouse.move(box.x + 200, box.y + 200)
  await page.mouse.down()
  await page.mouse.move(box.x + 320, box.y + 240, { steps: 8 })
  await page.mouse.up()
  await expect(page.locator('.tut__task')).toContainText('that worked')
  await next(page).click()
  // Zoom
  await expect(page.locator('.tut__title')).toHaveText(/zoom/i)
  await page.mouse.move(box.x + 300, box.y + 300)
  await page.mouse.wheel(0, -200)
  await expect(page.locator('.tut__task')).toContainText('that worked')
  await next(page).click()
  // Explode slider, from the keyboard
  await expect(page.locator('.tut__title')).toHaveText(/pull it apart/i)
  await page.locator('#explode').focus()
  await page.keyboard.press('Home') // lessons now open fully exploded, so move it back together
  await expect(page.locator('.tut__task')).toContainText('that worked')
  await next(page).click()
  // Pick a stage
  await expect(page.locator('.tut__title')).toHaveText(/open a stage/i)
  await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: /Encoder/ }).click()
  await expect(page.locator('.tut__task')).toContainText('that worked')
  await next(page).click()
  await next(page).click() // panel
  await expect(page.locator('.tut__title')).toHaveText(/five ways/i)
  await expect(page.locator('.tut__list li')).toHaveCount(5)
  await next(page).click()
  // Tour play: the tutorial switches to Tour and waits for Play.
  await expect(page.locator('.tut__title')).toHaveText(/play the tour/i)
  await expect(page.getByRole('tab', { name: 'Tour', exact: true })).toHaveAttribute('aria-selected', 'true')
  await page.locator('.spanel__play').click()
  await expect(page.locator('.tut__task')).toContainText('that worked')
  await next(page).click()
  await next(page).click() // toolbar
  await expect(page.locator('.tut__title')).toHaveText(/ask the tutor/i)
  await next(page).click() // ask
  await next(page).click() // keyboard
  await expect(page.locator('.tut__title')).toHaveText(/you are ready/i)
  await next(page).click() // Finish
  await expect(card(page)).toBeHidden()
  // Finishing stops the tour that was playing and returns to Explore.
  await expect(page.getByRole('tab', { name: 'Explore', exact: true })).toHaveAttribute('aria-selected', 'true')
  await page.reload()
  await page.waitForTimeout(2200)
  await expect(card(page)).toBeHidden()
})

test('the tutorial can go back, is a labelled modal, and dims everything else', async ({ page }) => {
  await page.goto('/lessons/tokenization')
  await next(page).click()
  await next(page).click()
  await page.getByRole('button', { name: 'Back', exact: true }).click()
  await expect(page.locator('.tut__title')).toHaveText(/turn the machine/i)
  await expect(card(page)).toHaveAttribute('aria-modal', 'true')
  // Clicking the dimmed page behind the spotlight does nothing.
  const hit = await page.evaluate(() => {
    const r = document.querySelector('.cine__modes')!.getBoundingClientRect()
    return document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2)?.className
  })
  expect(String(hit)).toContain('tut__dim')
})

test('tour play shows a visible playing state and a countdown, and pause stops it', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('explodeai.tutorial', 'done'))
  await page.goto('/lessons/embeddings')
  await page.getByRole('tab', { name: 'Tour', exact: true }).click()
  await expect(page.locator('.spanel__tour-state')).toContainText('PAUSED')
  await page.locator('.spanel__play').click()
  await expect(page.locator('.spanel__tour-state')).toContainText('PLAYING')
  await expect(page.locator('.spanel__countdown')).toBeVisible()
  await page.locator('.spanel__play').click()
  await expect(page.locator('.spanel__tour-state')).toContainText('PAUSED')
  await expect(page.locator('.spanel__countdown')).toHaveCount(0)
})
