import { expect, test } from '@playwright/test'

test('lesson fits a phone screen without horizontal scrolling', async ({ page }) => {
  await page.goto('/lessons/rag-pipeline')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow).toBeLessThanOrEqual(0)
  // Every primary control stays reachable and at least 40px tall for touch.
  for (const name of ['Explore', 'Tour', 'Experiment']) {
    const box = await page.getByRole('tab', { name }).boundingBox()
    expect(box!.height).toBeGreaterThanOrEqual(40)
  }
  await page.getByRole('tab', { name: 'Experiment' }).click()
  await expect(page.getByRole('tab', { name: 'Chunks' })).toBeVisible()
  const overflowAfter = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflowAfter).toBeLessThanOrEqual(0)
})
