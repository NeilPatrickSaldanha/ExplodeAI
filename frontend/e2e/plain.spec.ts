import { expect, test } from '@playwright/test'

const WEB_PORT = Number(process.env.E2E_WEB_PORT ?? 5174)

// The default voice: everyday words first, the standard name shown beside each one.
test.use({
  storageState: {
    cookies: [],
    origins: [{ origin: `http://127.0.0.1:${WEB_PORT}`, localStorage: [{ name: 'explodeai.tutorial', value: 'done' }] }],
  },
})

const LESSONS = [
  {
    path: '/lessons/embeddings',
    stage: /Word chopper/,
    everyday: 'Word chopper',
    technical: 'Tokenizer',
    control: 'How closeness is measured',
    controlTech: 'Similarity',
    tab: 'Meaning map',
    term: 'Token',
    banned: /\b(cosine|PCA|pooling|vectors?)\b/i,
  },
]

for (const l of LESSONS) {
  test(`${l.path}: plain words first, the technical name beside them`, async ({ page }) => {
    await page.goto(l.path)
    // The page's own summary line carries none of the lesson's technical words.
    await expect(page.locator('.cine__head')).not.toContainText(l.banned)
    await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: l.stage }).click()
    await expect(page.locator('.cine__panel .spanel__title')).toHaveText(l.everyday)
    await expect(page.locator('.cine__panel .spanel__tech')).toContainText(l.technical)
    const terms = page.locator('.cine__panel .understand__terms')
    await expect(terms).toContainText('WORDS YOU WILL HEAR')
    await expect(terms).toContainText(l.term)
    // The experiment's controls and tabs use everyday names and keep the technical one small beside them.
    await page.getByRole('tab', { name: 'Experiment', exact: true }).click()
    await expect(page.getByRole('group', { name: new RegExp(`${l.control} \\(${l.controlTech}\\)`) })).toBeVisible()
    await expect(page.getByRole('tab', { name: new RegExp(l.tab) })).toBeVisible()
  })

  test(`${l.path}: the switch gives the technical names back, and remembers the choice`, async ({ page }) => {
    await page.goto(l.path)
    await expect(page.getByRole('button', { name: 'Plain words' })).toHaveAttribute('aria-pressed', 'true')
    await page.getByRole('button', { name: 'Technical names' }).click()
    await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: new RegExp(l.technical) }).click()
    await expect(page.locator('.cine__panel .spanel__title')).toHaveText(l.technical)
    await expect(page.locator('.cine__panel .spanel__tech')).toHaveCount(0)
    await page.reload()
    await expect(page.getByRole('button', { name: 'Technical names' })).toHaveAttribute('aria-pressed', 'true')
  })
}

test('the home page tells the lessons in plain words too', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.lesson-link__summary').nth(2)).toContainText('list of 384 numbers')
})
