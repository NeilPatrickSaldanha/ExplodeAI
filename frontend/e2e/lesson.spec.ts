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

test('3D view renders and parts are selectable from the list and keyboard', async ({ page }) => {
  await page.goto(LESSON)
  await expect(page.locator('.exploded-view[data-mode="3d"] canvas')).toBeVisible()
  await expect(page.getByText('Verified: 32/32 claims through all three passes')).toBeVisible()
  // Live values from a real run appear on the selected part's label.
  await page.getByRole('navigation', { name: 'Parts' }).getByRole('button', { name: /Chunker/ }).click()
  await expect(page.locator('.part-label', { hasText: 'Chunker' })).toContainText('CHUNKS')

  await page.getByRole('navigation', { name: 'Parts' }).getByRole('button', { name: /Retriever/ }).click()
  const panel = page.getByRole('region', { name: 'Lesson activities' })
  await expect(panel.getByRole('heading', { name: 'Retriever' })).toBeVisible()
  await expect(panel.locator('.claim').first()).toBeVisible()
  await expect(panel.locator('a.claim__source').first()).toHaveAttribute('href', /^https?:\/\//)

  // Keyboard: focus the scene, arrow to the next part.
  await page.locator('.exploded-view').focus()
  await page.keyboard.press('ArrowRight')
  await expect(panel.getByRole('heading', { name: 'Prompt assembler' })).toBeVisible()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('button', { name: /Isolate/ })).toHaveAttribute('aria-pressed', 'true')
  await page.keyboard.press('Escape')
  await expect(page.getByText('No part selected.')).toBeAttached()
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
  await expect(page.locator('.lesson__status')).toContainText('FIXED 1/4')

  await page.reload()
  await expect(page.locator('.lesson__status')).toContainText('FIXED 1/4')
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
  await expect(page.locator('.lesson__status')).toContainText('REBUILT YES')
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

test('tour steps through every stage and isolates it', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Tour')
  await expect(page.getByText('STEP 1 OF 8')).toBeVisible()
  for (let i = 2; i <= 8; i++) {
    await page.getByRole('button', { name: /Next/ }).click()
    await expect(page.getByText(`STEP ${i} OF 8`)).toBeVisible()
  }
  await expect(page.getByRole('button', { name: /Next/ })).toBeDisabled()
})
