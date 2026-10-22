import { expect, test, type Page } from '@playwright/test'

/** Layout checks at the sizes people actually use: small phone, common phones, landscape, tablet. */
const SIZES = [
  { name: 'small phone 320', width: 320, height: 568 },
  { name: 'iPhone SE 375', width: 375, height: 667 },
  { name: 'large phone 430', width: 430, height: 932 },
  { name: 'phone landscape', width: 844, height: 390 },
  { name: 'tablet 768', width: 768, height: 1024 },
]
const LESSONS = ['rag-pipeline', 'tokenization', 'embeddings', 'attention', 'agents']

/** Interactive elements that stick out past the right edge and are not inside a scroller. */
async function clippedControls(page: Page) {
  return page.evaluate(() => {
    const vw = document.documentElement.clientWidth
    const inScroller = (el: Element) => {
      for (let p = el.parentElement; p; p = p.parentElement) {
        const o = getComputedStyle(p).overflowX
        if ((o === 'auto' || o === 'scroll') && p.scrollWidth > p.clientWidth) return true
      }
      return false
    }
    const bad: string[] = []
    for (const el of document.querySelectorAll('.cine button, .cine a[href], .cine summary, .cine [role=tab]')) {
      const r = el.getBoundingClientRect()
      if (r.width && r.right > vw + 1 && !inScroller(el)) bad.push(`${(el.textContent ?? '').trim().slice(0, 30)} → ${Math.round(r.right)} > ${vw}`)
    }
    return bad
  })
}

for (const size of SIZES) {
  test.describe(size.name, () => {
    test.use({ viewport: { width: size.width, height: size.height }, hasTouch: true, isMobile: size.width < 800 })

    for (const lesson of LESSONS) {
      test(`${lesson}: nothing is clipped or scrolls sideways, with a stage open`, async ({ page }) => {
        await page.goto(`/lessons/${lesson}`)
        await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
        await page.locator('.stagebar button').nth(2).click()
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
        expect(overflow).toBeLessThanOrEqual(0)
        expect(await clippedControls(page)).toEqual([])
        // The five modes are all reachable.
        for (const mode of ['Explore', 'Tour', 'Experiment', 'Break & fix', 'Rebuild']) {
          await expect(page.getByRole('tab', { name: mode, exact: true })).toBeAttached()
        }
      })
    }

    test('the tutor keeps room for the conversation, its chips and its input', async ({ page }) => {
      await page.goto('/lessons/attention')
      await page.getByRole('button', { name: 'Ask ExplodeAI' }).click()
      await page.getByLabel('Your question').fill('What are the lessons?')
      await page.getByRole('button', { name: 'Ask', exact: true }).click()
      await expect(page.locator('.tmsg--overview')).toBeVisible()
      const m = await page.evaluate(() => {
        const h = (s: string) => document.querySelector(s)!.getBoundingClientRect()
        const panel = h('.tutor')
        return { panel, log: h('.tutor__log').height, chips: h('.tutor__chips').height, input: h('#tutor-input'), vw: innerWidth, vh: innerHeight }
      })
      expect(m.log).toBeGreaterThanOrEqual(m.vh < 500 ? 70 : 110)
      expect(m.chips).toBeGreaterThanOrEqual(36)
      expect(m.input.height).toBeGreaterThanOrEqual(36)
      expect(m.panel.left).toBeGreaterThanOrEqual(0)
      expect(m.panel.right).toBeLessThanOrEqual(m.vw)
      expect(m.panel.top).toBeGreaterThanOrEqual(0)
      expect(m.input.bottom).toBeLessThanOrEqual(m.vh)
    })
  })
}

test.describe('phone tutor behaviour', () => {
  test.use({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true })

  test('the floating button is icon-only and does not stay open on the next page', async ({ page }) => {
    await page.goto('/lessons/attention')
    const fab = page.getByRole('button', { name: 'Ask ExplodeAI' })
    const box = (await fab.boundingBox())!
    expect(box.width).toBeLessThanOrEqual(60)
    expect(box.height).toBeGreaterThanOrEqual(44)
    await fab.click()
    await expect(page.locator('.tutor')).toBeVisible()
    await page.goto('/lessons/tokenization')
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    await expect(page.locator('.tutor')).toHaveCount(0)
    await expect(page.getByRole('button', { name: 'Ask ExplodeAI' })).toHaveAttribute('aria-expanded', 'false')
  })
})
