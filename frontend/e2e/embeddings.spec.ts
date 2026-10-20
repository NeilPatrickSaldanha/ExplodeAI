import { expect, test, type Page } from '@playwright/test'

const LESSON = '/lessons/embeddings'

const panel = (page: Page) => page.locator('.cine__panel')
const stages = (page: Page) => page.getByRole('navigation', { name: 'Pipeline stages' })
const openMode = (page: Page, name: string) => page.getByRole('tab', { name, exact: true }).click()

test('home lists lesson 03 after lesson 02 and it opens', async ({ page }) => {
  await page.goto('/')
  const link = page.getByRole('link', { name: /embeddings, exploded/i })
  await expect(link).toContainText('03 ·')
  await link.click()
  await expect(page).toHaveURL(new RegExp(`${LESSON}$`))
})

test('3D view renders and stages show live readouts and cited claims', async ({ page }) => {
  await page.goto(LESSON)
  await expect(page.locator('.exploded-view[data-mode="3d"] canvas')).toBeVisible()
  await expect(page.locator('.cine__meta')).toContainText(/(\d+)\/\1 claims through all three passes/)
  await stages(page).getByRole('button', { name: /Encoder/ }).click()
  await expect(panel(page).getByRole('heading', { name: 'Encoder' })).toBeVisible()
  await expect(panel(page).getByText('STAGE 04 / 08')).toBeVisible()
  await panel(page).locator('.fact__head').first().click()
  await expect(panel(page).locator('a.claim__source').first()).toHaveAttribute('href', /^https?:\/\//)
})

test('experiment: real model finds the bookshelf by meaning, with a table fallback', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await page.getByRole('button', { name: 'Bookshelf' }).click()
  await expect(page.locator('#emb-text')).toHaveValue('a place to put my books')
  await page.getByRole('tab', { name: 'Neighbours' }).click()
  await expect(page.locator('.neigh li').first()).toContainText('bookshelf')
  await expect(page.getByText('384-D · NEURAL')).toBeVisible()
  // Lexical matching shares no word with the bookshelf sentence, so every score is 0.
  await page.getByRole('radio', { name: 'Lexical' }).first().click()
  await page.getByRole('radio', { name: 'Lexical' }).last().click()
  await expect(page.locator('.neigh__score').first()).toHaveText('0.000')
})

test('semantic space states its approximation and offers a table', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await page.getByRole('tab', { name: 'Semantic space' }).click()
  await expect(page.locator('.sspace__bar')).toContainText(/PCA → 3D · \d+% OF VARIANCE KEPT/)
  await page.getByRole('button', { name: 'Show as table' }).click()
  await expect(page.locator('table.ranking tbody tr')).toHaveCount(24)
})

test('long text is cut at 512 tokens and the lesson says so', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await page.getByRole('button', { name: 'Long text' }).click()
  await page.getByRole('tab', { name: 'Tokens' }).click()
  await expect(page.getByText(/the rest was cut off before the model saw it/)).toBeVisible()
})

test('what breaks if removed: the pipeline really runs without pooling', async ({ page }) => {
  await page.goto(LESSON)
  await stages(page).getByRole('button', { name: /Pooling/ }).click()
  await panel(page).getByRole('button', { name: 'Run without the pooling' }).click()
  const compare = panel(page).locator('.breaks__compare')
  await expect(compare).toContainText('Real execution, stage removed')
  await expect(compare.locator('.outcome--broken')).toContainText(/token vectors/)
})

test('break & fix: mixed models fail, then pass once both sides use the neural model', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Break & fix')
  await page.getByRole('button', { name: /Two models, one search/ }).click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Still broken.')
  await page.getByRole('radio', { name: /Neural/ }).last().click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Fixed.')
})

test('tour walks all eight stages', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Tour')
  await expect(page.getByText('TOUR · STEP 1 OF 8')).toBeVisible()
  for (let i = 2; i <= 8; i++) {
    await panel(page).getByRole('button', { name: 'Next stage' }).click()
    await expect(page.getByText(`TOUR · STEP ${i} OF 8`)).toBeVisible()
  }
})
