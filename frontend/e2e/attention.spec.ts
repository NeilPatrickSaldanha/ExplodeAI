import { expect, test, type Page } from '@playwright/test'

const LESSON = '/lessons/attention'
const panel = (page: Page) => page.locator('.cine__panel')
const stages = (page: Page) => page.getByRole('navigation', { name: 'Pipeline stages' })
const openMode = (page: Page, name: string) => page.getByRole('tab', { name, exact: true }).click()
const seg = (page: Page, group: string, option: string) => page.getByRole('group', { name: group }).getByRole('radio', { name: option, exact: true })

test('home lists lesson 04 and it opens with its 3D scene and cited stages', async ({ page }) => {
  await page.goto('/')
  const link = page.getByRole('link', { name: /attention, exploded/i })
  await expect(link).toContainText('04 ·')
  await link.click()
  await expect(page).toHaveURL(new RegExp(`${LESSON}$`))
  await expect(page.locator('.exploded-view[data-mode="3d"] canvas')).toBeVisible()
  await stages(page).getByRole('button', { name: /Score grid/ }).click()
  await expect(panel(page).getByRole('heading', { name: 'Score grid' })).toBeVisible()
  await expect(panel(page).getByText('STAGE 04 / 08')).toBeVisible()
  await panel(page).locator('.fact__head').first().click()
  await expect(panel(page).locator('a.claim__source').first()).toHaveAttribute('href', /^https?:\/\//)
})

test('experiment: a real toy layer, labelled as such, with rows that add up to 100%', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await expect(page.getByText('REAL EXECUTION · TOY LAYER')).toBeVisible()
  await expect(panel(page).getByRole('note')).toContainText('not a trained model')
  const table = panel(page).locator('table.agrid__table')
  await expect(table.locator('tbody tr')).toHaveCount(6)
  await expect(table.locator('thead th')).toHaveCount(6)
  // Without a mask nothing is hidden; each row's printed numbers add up to about 100.
  await expect(table.locator('.is-hidden')).toHaveCount(0)
  const row = await table.locator('tbody tr').nth(2).locator('.agrid__num').allTextContents()
  const sum = row.reduce((a, b) => a + Number(b), 0)
  expect(sum).toBeGreaterThan(94)
  expect(sum).toBeLessThan(106)
})

test('causal mask hides later words with a hatch and a dash, not colour alone', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await seg(page, 'Causal mask (hide later words)', 'On').click()
  const hidden = panel(page).locator('table.agrid__table .is-hidden')
  await expect(hidden).toHaveCount(15) // upper triangle of a 6 x 6 grid
  await expect(hidden.first()).toContainText('–')
  await expect(panel(page).getByText('Attention on later words')).toBeVisible()
  await expect(panel(page).locator('.outcome__stats dd').nth(3)).toHaveText('0%')
})

test('one word view: pick who is looking and read where its attention goes', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await page.getByRole('tab', { name: 'One word' }).click()
  await page.getByRole('button', { name: /^mat/ }).click()
  await expect(panel(page).locator('.look__note')).toContainText('“mat” builds its new vector')
  await expect(panel(page).locator('.look__list li')).toHaveCount(4)
})

test('what breaks if removed: softmax really is skipped and rows stop adding up to 1', async ({ page }) => {
  await page.goto(LESSON)
  await stages(page).getByRole('button', { name: /Softmax/ }).click()
  await panel(page).getByRole('button', { name: 'Run without the softmax' }).click()
  const compare = panel(page).locator('.breaks__compare')
  await expect(compare).toContainText('Real execution, step removed')
  await expect(compare.locator('.outcome--broken')).toContainText('Some weights are negative')
})

test('break & fix: saturated softmax fails, then scaling fixes it; position fixes order-blindness', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Break & fix')
  await page.getByRole('button', { name: /One word takes everything/ }).click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Still broken.')
  await seg(page, 'Scale scores by 1/√d_k', 'On').click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Fixed.')
  await page.getByRole('button', { name: '← All challenges' }).click()
  await page.getByRole('button', { name: /Order-blind attention/ }).click()
  await expect(seg(page, 'Position vectors', 'Off')).toHaveAttribute('aria-checked', 'true')
  await seg(page, 'Position vectors', 'On').click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Fixed.')
})

test('rebuild and tour reach all eight steps', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Tour')
  for (let i = 2; i <= 8; i++) {
    await panel(page).getByRole('button', { name: 'Next stage' }).click()
    await expect(page.getByText(`TOUR · STEP ${i} OF 8`)).toBeVisible()
  }
})
