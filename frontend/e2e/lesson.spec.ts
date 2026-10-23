import { expect, test, type Page } from '@playwright/test'

const LESSON = '/lessons/rag-pipeline'

async function openMode(page: Page, name: string) {
  await page.getByRole('tab', { name }).click()
}

test('home lists the published lesson and links to it', async ({ page }) => {
  await page.goto('/')
  const link = page.getByRole('link', { name: /retrieval-augmented generation/i })
  await expect(link).toBeVisible()
  await expect(link).not.toContainText('DRAFT')
  await link.click()
  await expect(page).toHaveURL(new RegExp(`${LESSON}$`))
  await expect(page.getByRole('heading', { level: 1 })).toContainText('exploded')
})

const stages = (page: Page) => page.getByRole('navigation', { name: 'Pipeline stages' })
const panel = (page: Page) => page.locator('.cine__panel')

test('hero scene renders; stages are selectable from the stage bar, the scene and the keyboard', async ({ page }) => {
  await page.goto(LESSON)
  await expect(page.locator('.exploded-view[data-mode="3d"] canvas')).toBeVisible()
  await expect(page.getByText('Verified: 33/33 claims through all three passes')).toBeVisible()
  await expect(page.getByRole('list', { name: 'Flow legend' })).toContainText('Vector flow')

  // Live values from a real run appear on the selected part's callout.
  await stages(page).getByRole('button', { name: /Chunker/ }).click()
  await expect(page.locator('.callout', { hasText: 'Chunker' })).toContainText('CHUNKS')
  await expect(stages(page).getByRole('button', { name: /Chunker/ })).toHaveAttribute('aria-current', 'step')

  await stages(page).getByRole('button', { name: /Retriever/ }).click()
  await expect(panel(page).getByRole('heading', { name: 'Retriever' })).toBeVisible()
  await expect(panel(page).getByText('STAGE 06 / 08')).toBeVisible()
  // What goes in / comes out uses real scores from the run.
  await expect(panel(page).locator('.io-list__score').first()).toHaveText(/^0\.\d{3}$/)
  // Facts expand to their citations.
  await panel(page).locator('.fact__head').first().click()
  await expect(panel(page).locator('a.claim__source').first()).toHaveAttribute('href', /^https?:\/\//)

  // Stage bar keyboard: arrow right moves and selects.
  await stages(page).getByRole('button', { name: /Retriever/ }).focus()
  await page.keyboard.press('ArrowRight')
  await expect(panel(page).getByRole('heading', { name: 'Prompt assembler' })).toBeVisible()

  // Scene keyboard: focus the scene, arrow to the next part, Enter isolates, Esc clears.
  await page.locator('.exploded-view').focus()
  await page.keyboard.press('ArrowRight')
  await expect(panel(page).getByRole('heading', { name: 'Generator' })).toBeVisible()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('button', { name: /Isolate/ })).toHaveAttribute('aria-pressed', 'true')
  await page.keyboard.press('Escape')
  await expect(page.getByText('No part selected.')).toBeAttached()
})

test('what breaks if removed: the pipeline really runs without the stage', async ({ page }) => {
  await page.goto(LESSON)
  await stages(page).getByRole('button', { name: /Vector index/ }).click()
  await panel(page).getByRole('button', { name: 'Run without the vector index' }).click()
  const compare = panel(page).locator('.breaks__compare')
  await expect(compare).toContainText('Real execution, stage removed')
  await expect(compare.locator('.outcome').first().locator('.is-pass')).toBeVisible()
  await expect(compare.locator('.outcome--broken')).toContainText('nothing is stored to search')
})

test('tour stays in sync when you click a stage directly', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Tour')
  await expect(page.getByText('TOUR · STEP 1 OF 8')).toBeVisible()
  await stages(page).getByRole('button', { name: /Retriever/ }).click()
  await expect(page.getByText('TOUR · STEP 6 OF 8')).toBeVisible()
  await expect(panel(page).getByRole('heading', { name: 'Retriever' })).toBeVisible()
  await expect(panel(page).locator('.spanel__tour-title')).toContainText(/rank/i)
})

test('experiment runs for real and exposes chunks, ranking, prompt and answer', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await page.getByRole('button', { name: 'Battery storage' }).click()
  await expect(page.getByRole('tab', { name: 'Chunks' })).toBeVisible()
  await page.getByRole('tab', { name: 'Ranking' }).click()
  await expect(page.locator('.ranking tr.is-hit').first()).toContainText('battery#')
  await page.getByRole('tab', { name: 'Prompt' }).click()
  await expect(page.getByLabel('Assembled prompt')).toContainText('<documents>')
  await page.getByRole('tab', { name: 'Answer' }).click()
  await expect(page.getByText('Real execution, not an LLM')).toBeVisible()
  await expect(page.locator('.answerview__text')).toContainText('40 and 60 percent')
})

test('break & fix: the broken pipeline fails, a keyboard fix passes, progress persists', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Break & fix')
  await page.getByRole('button', { name: /The fact that got cut in half/ }).click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.check')).toContainText('Still broken.')

  // Locked controls cannot be changed.
  await expect(page.getByLabel('Question')).toBeDisabled()

  const size = page.locator('#size')
  await size.focus()
  for (let i = 0; i < 12; i++) await page.keyboard.press('ArrowRight')
  await expect(size).toHaveAttribute('aria-valuenow', '20')
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.check')).toContainText('Fixed.')
  await expect(page.locator('.cine__meta')).toContainText('FIXED 1/4')

  await page.reload()
  await expect(page.locator('.cine__meta')).toContainText('FIXED 1/4')
})

test('rebuild: reorder with keyboard-accessible buttons until the pipeline can run', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Rebuild')
  const target = ['Knowledge source', 'Chunker', 'Chunk embedder', 'Vector index', 'Query embedder', 'Retriever', 'Prompt assembler', 'Generator']
  await page.getByRole('button', { name: 'Check order' }).click()
  await expect(page.locator('.rebuild .check')).toContainText('run before something they need')

  for (let pos = 0; pos < target.length; pos++) {
    const names = await page.locator('.rebuild__name').allTextContents()
    let at = names.indexOf(target[pos])
    while (at > pos) {
      await page.getByRole('button', { name: `Move ${target[pos]} up` }).click()
      at--
    }
  }
  await page.getByRole('button', { name: 'Check order' }).click()
  await expect(page.locator('.rebuild .check')).toContainText('Every stage runs after what it depends on.')
  await expect(page.locator('.cine__meta')).toContainText('REBUILT YES')
})

test('2D mode and reduced motion are available as alternatives', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto(LESSON)
  await expect(page.getByRole('button', { name: /Calm/ })).toHaveAttribute('aria-pressed', 'true')
  await page.getByRole('button', { name: /3D/ }).click()
  const diagram = page.locator('.flat-diagram')
  await expect(diagram).toBeVisible()
  const part = diagram.getByRole('button', { name: /Vector index/ })
  await part.focus()
  await page.keyboard.press('Enter')
  await expect(part).toHaveAttribute('aria-pressed', 'true')
})

test('tour steps through every stage with next/back', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Tour')
  await expect(page.getByText('TOUR · STEP 1 OF 8')).toBeVisible()
  for (let i = 2; i <= 8; i++) {
    await panel(page).getByRole('button', { name: 'Next stage' }).click()
    await expect(page.getByText(`TOUR · STEP ${i} OF 8`)).toBeVisible()
  }
  await expect(panel(page).getByRole('button', { name: 'Next stage' })).toBeDisabled()
  await panel(page).getByRole('button', { name: 'Previous stage' }).click()
  await expect(page.getByText('TOUR · STEP 7 OF 8')).toBeVisible()
})

test('isolate needs a selected stage, says so when there is none, and works once one is picked', async ({ page }) => {
  await page.goto('/lessons/tokenization')
  const iso = page.getByRole('button', { name: /Isolate/ })
  await expect(page.locator('.part-label.is-selected')).toHaveCount(1) // stage 1 is shown on load
  await iso.click()
  await expect(iso).toHaveAttribute('aria-pressed', 'true')
  await expect(page.locator('.part-label.is-dim').first()).toBeVisible()
  // Clicking empty space clears the selection; Isolate must then be disabled, with a reason.
  await page.locator('.cine__frame canvas').click({ position: { x: 30, y: 300 } })
  await expect(page.locator('.part-label.is-selected')).toHaveCount(0)
  await expect(iso).toBeDisabled()
  await expect(iso).toHaveAttribute('title', 'Select a stage first, then isolate it')
  await expect(page.locator('.part-label.is-dim')).toHaveCount(0)
  await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: /Encoder/ }).click()
  await expect(iso).toBeEnabled()
  await iso.click()
  await expect(iso).toHaveAttribute('aria-pressed', 'true')
})


test('the footer credits the creator quietly', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('footer.foot')).toContainText('Made by Neil')
})
