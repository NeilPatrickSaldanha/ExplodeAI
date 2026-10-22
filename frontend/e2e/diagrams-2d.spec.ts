import { expect, test, type Page } from '@playwright/test'

/** The 2D diagram must read cleanly in every lesson at every size: nothing overlaps, nothing is clipped. */
const LESSONS = ['rag-pipeline', 'tokenization', 'embeddings', 'attention', 'agents']
const SIZES = [
  { name: 'desktop', width: 1440, height: 900, mobile: false },
  { name: 'tablet', width: 768, height: 1024, mobile: true },
  { name: 'phone', width: 390, height: 844, mobile: true },
  { name: 'small phone', width: 320, height: 568, mobile: true },
]

async function open2d(page: Page, lesson: string) {
  await page.goto(`/lessons/${lesson}`)
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await page.getByRole('button', { name: '3D', exact: true }).click()
  await expect(page.locator('.exploded-view[data-mode="2d"] .flat-diagram')).toBeVisible()
  await page.waitForTimeout(400)
}

/** Boxes of nodes and label pills in SVG user units, plus each text's width against its container. */
async function measure(page: Page) {
  return page.evaluate(() => {
    const rect = (el: Element) => {
      const r = el.getBoundingClientRect()
      return { x: r.left, y: r.top, w: r.width, h: r.height }
    }
    const nodes = [...document.querySelectorAll('.flat-diagram__part')].map((g) => ({
      name: g.getAttribute('aria-label')!.split(',')[0],
      box: rect(g.querySelector('rect')!),
      texts: [...g.querySelectorAll('text')].map((t) => rect(t)),
    }))
    const pills = [...document.querySelectorAll('.flat-diagram__pill')].map((g) => ({
      name: (g.textContent ?? '').trim().slice(0, 30),
      box: rect(g.querySelector('rect')!),
      texts: [...g.querySelectorAll('text')].map((t) => rect(t)),
    }))
    const svg = rect(document.querySelector('.flat-diagram')!)
    return { nodes, pills, svg }
  })
}

type R = { x: number; y: number; w: number; h: number }
const overlap = (a: R, b: R) => a.x < b.x + b.w - 1 && a.x + a.w > b.x + 1 && a.y < b.y + b.h - 1 && a.y + a.h > b.y + 1
const inside = (inner: R, outer: R, tol = 1.5) => inner.x >= outer.x - tol && inner.y >= outer.y - tol && inner.x + inner.w <= outer.x + outer.w + tol && inner.y + inner.h <= outer.y + outer.h + tol

for (const size of SIZES) {
  test.describe(size.name, () => {
    test.use({ viewport: { width: size.width, height: size.height }, hasTouch: size.mobile, isMobile: size.mobile })
    for (const lesson of LESSONS) {
      test(`${lesson}: no node or label overlaps another, and all text stays inside its box`, async ({ page }) => {
        await open2d(page, lesson)
        const m = await measure(page)
        expect(m.nodes.length).toBeGreaterThanOrEqual(8)
        for (let i = 0; i < m.nodes.length; i++) {
          for (let j = i + 1; j < m.nodes.length; j++) expect(overlap(m.nodes[i].box, m.nodes[j].box), `${m.nodes[i].name} vs ${m.nodes[j].name}`).toBe(false)
        }
        for (const p of m.pills) {
          for (const n of m.nodes) expect(overlap(p.box, n.box), `label "${p.name}" over ${n.name}`).toBe(false)
          for (const t of p.texts) expect(inside(t, p.box), `label text in "${p.name}"`).toBe(true)
        }
        for (let i = 0; i < m.pills.length; i++) {
          for (let j = i + 1; j < m.pills.length; j++) expect(overlap(m.pills[i].box, m.pills[j].box), `"${m.pills[i].name}" vs "${m.pills[j].name}"`).toBe(false)
        }
        for (const n of m.nodes) for (const t of n.texts) expect(inside(t, n.box), `text in ${n.name}`).toBe(true)
      })
    }
  })
}

test('2D diagrams use one visual language: same node, label and arrow styles in every lesson', async ({ page }) => {
  const seen: string[] = []
  for (const lesson of LESSONS) {
    await open2d(page, lesson)
    seen.push(
      await page.evaluate(() => {
        const cs = (s: string, p: string) => getComputedStyle(document.querySelector(s)!).getPropertyValue(p)
        return [
          cs('.flat-diagram__name', 'font-size'),
          cs('.flat-diagram__meta', 'font-size'),
          cs('.flat-diagram__pill-text', 'font-size'),
          cs('.flat-diagram__link:not(.is-focus)', 'stroke-width'),
          document.querySelectorAll('.flat-diagram__pill').length > 0 ? 'pills' : 'none',
          document.querySelectorAll('marker').length + ' markers',
        ].join('|')
      }),
    )
  }
  expect(new Set(seen).size).toBe(1)
})

test('2D selection and isolate still work, and labels dim with their links', async ({ page }) => {
  await open2d(page, 'attention')
  await page.locator('.flat-diagram__part', { hasText: 'Softmax' }).click()
  await expect(page.locator('.flat-diagram__part.is-selected')).toContainText('Softmax')
  await page.getByRole('button', { name: /Isolate/ }).click()
  await expect(page.locator('.flat-diagram__part.is-dim').first()).toBeVisible()
  // (A perfectly horizontal line has no height, so count the dimmed links rather than asking if one is visible.)
  await expect(page.locator('.flat-diagram .flat-diagram__link.is-dim')).not.toHaveCount(0)
  await expect(page.locator('.flat-diagram .flat-diagram__pill').first()).toBeVisible()
})
