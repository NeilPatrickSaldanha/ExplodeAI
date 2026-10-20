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

test('tokenization lesson fits a phone screen without horizontal scrolling', async ({ page }) => {
  await page.goto('/lessons/tokenization')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  const overflow = () => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(await overflow()).toBeLessThanOrEqual(0)
  await page.getByRole('tab', { name: 'Experiment' }).click()
  await page.getByRole('button', { name: 'Accents and emoji' }).click()
  await expect(page.locator('.tokstrip .check')).toContainText('Round trip exact')
  for (const name of ['Replay', 'Merges', 'Trade-off']) {
    await page.getByRole('tab', { name }).click()
    expect(await overflow()).toBeLessThanOrEqual(0)
  }
  const box = await page.getByRole('button', { name: 'Accents and emoji' }).boundingBox()
  expect(box!.height).toBeGreaterThanOrEqual(40)
})

test.describe('first visit on a phone', () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test('the tutorial is a bottom sheet with big buttons, and the page never scrolls sideways', async ({ page }) => {
    await page.goto('/lessons/embeddings')
    const card = page.getByRole('dialog')
    await expect(card).toBeVisible()
    const overflow = () => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
    expect(await overflow()).toBeLessThanOrEqual(0)
    const vh = page.viewportSize()!.height
    const cardBox = (await card.boundingBox())!
    expect(cardBox.y + cardBox.height).toBeLessThanOrEqual(vh)
    for (const name of ['Skip', 'Start']) {
      const box = (await page.getByRole('button', { name, exact: true }).first().boundingBox())!
      expect(box.height).toBeGreaterThanOrEqual(40)
    }
    await page.locator('.tut__next').click()
    await expect(page.locator('.tut__ring')).toBeVisible()
    await page.getByRole('button', { name: 'Skip the tutorial' }).click()
    await expect(card).toBeHidden()
  })
})

test('stage explanations work on a phone: sections open, the demo plays, no sideways scroll', async ({ page }) => {
  await page.goto('/lessons/embeddings')
  await page.getByRole('button', { name: /Pooling/ }).first().click()
  const understand = page.locator('.understand')
  await understand.scrollIntoViewIfNeeded()
  await understand.getByRole('button', { name: 'Play', exact: true }).click()
  await expect(understand.locator('.demo__steps li.is-on').first()).toBeVisible()
  const summary = understand.locator('summary', { hasText: 'Why it is needed' })
  expect((await summary.boundingBox())!.height).toBeGreaterThanOrEqual(40)
  await summary.click()
  await expect(understand.getByText('To compare whole sentences')).toBeVisible()
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow).toBeLessThanOrEqual(0)
})
