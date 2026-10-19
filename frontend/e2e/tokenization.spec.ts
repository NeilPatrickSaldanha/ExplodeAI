import { expect, test, type Page } from '@playwright/test'

const LESSON = '/lessons/tokenization'

async function openMode(page: Page, name: string) {
  await page.getByRole('tab', { name, exact: true }).click()
}

const panel = (page: Page) => page.getByRole('region', { name: 'Lesson activities' })

test('home lists lesson 02 and it opens', async ({ page }) => {
  await page.goto('/')
  const link = page.getByRole('link', { name: /tokenization, exploded/i })
  await expect(link).toBeVisible()
  await expect(link).toContainText('02 ·')
  await link.click()
  await expect(page).toHaveURL(new RegExp(`${LESSON}$`))
  await expect(page.getByRole('heading', { level: 1 })).toContainText('tokenization')
})

test('3D view renders, parts carry live readouts and cited claims', async ({ page }) => {
  await page.goto(LESSON)
  await expect(page.locator('.exploded-view[data-mode="3d"] canvas')).toBeVisible()
  await expect(page.locator('.lesson__status')).toContainText(/Verified: (\d+)\/\1 claims through all three passes/)
  await page.getByRole('navigation', { name: 'Parts' }).getByRole('button', { name: /Base alphabet/ }).click()
  await expect(page.locator('.part-label', { hasText: 'Base alphabet' })).toContainText('256 SYMBOLS')
  await expect(panel(page).getByRole('heading', { name: 'Base alphabet' })).toBeVisible()
  await expect(panel(page).locator('a.claim__source').first()).toHaveAttribute('href', /^https?:\/\//)

  await page.locator('.exploded-view').focus()
  await page.keyboard.press('ArrowRight')
  await expect(panel(page).getByRole('heading', { name: 'Merge learner' })).toBeVisible()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('button', { name: /Isolate/ })).toHaveAttribute('aria-pressed', 'true')
})

test('experiment: byte alphabet round-trips accents, the character alphabet loses them', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await expect(page.getByText('Real execution · educational BPE')).toBeVisible()
  await page.getByRole('button', { name: 'Accents and emoji' }).click()
  await expect(page.getByLabel('Text to tokenize')).toHaveValue('Café crème at the lantern ☕')
  const verdict = page.locator('.tokstrip .check')
  await expect(verdict).toContainText('Round trip exact')
  await expect(page.locator('.tok--partial').first()).toBeVisible()

  await page.getByRole('radio', { name: 'Training characters' }).click()
  await expect(verdict).toContainText('Round trip fails')
  await expect(page.locator('.tok--unk').first()).toContainText('UNKNOWN')
})

test('experiment: merges table, replay by keyboard, and trade-off with a data table', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await page.getByRole('tab', { name: 'Merges' }).click()
  await expect(page.getByRole('region', { name: 'Learned merges in order' })).toContainText('·keeper')

  await page.getByRole('tab', { name: 'Replay' }).click()
  await expect(page.getByRole('button', { name: 'Play replay' })).toHaveCount(0)
  await page.getByRole('button', { name: 'Previous merge' }).focus()
  await page.keyboard.press('Enter')
  await expect(page.locator('.replay__now')).toContainText(/Step \d+: merge rank/)

  await page.getByRole('tab', { name: 'Trade-off' }).click()
  await expect(page.getByRole('img', { name: /Line chart/ })).toBeVisible()
  await expect(page.getByRole('region', { name: 'Trade-off data' })).toContainText('(yours)')
})

test('break & fix: unknown characters fail, a keyboard fix passes, progress persists', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Break & fix')
  await page.getByRole('button', { name: /The characters that vanished/ }).click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Still broken.')
  await expect(page.getByLabel('Text to tokenize')).toBeDisabled()

  const bytes = page.getByRole('radio', { name: '256 bytes' })
  await bytes.focus()
  await page.keyboard.press('Enter')
  await expect(bytes).toHaveAttribute('aria-checked', 'true')
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Fixed.')
  await expect(page.locator('.lesson__status')).toContainText('FIXED 1/4')

  await page.reload()
  await expect(page.locator('.lesson__status')).toContainText('FIXED 1/4')
})

test('break & fix: the merges slider fixes the token budget from the keyboard', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Break & fix')
  await page.getByRole('button', { name: /Over the token budget/ }).click()
  const merges = page.locator('#merges')
  await merges.focus()
  await page.keyboard.press('End')
  await expect(merges).toHaveAttribute('aria-valuenow', '300')
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Fixed.')
})

test('rebuild: reorder the tokenizer stages with buttons', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Rebuild')
  const target = ['Training corpus', 'Pre-tokenizer', 'Base alphabet', 'Merge learner', 'Vocabulary', 'Input text', 'Encoder', 'Decoder']
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

test('tour walks all eight stages; 2D fallback is keyboard operable', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Tour')
  await expect(page.getByText('STEP 1 OF 8')).toBeVisible()
  for (let i = 2; i <= 8; i++) {
    await page.getByRole('button', { name: /Next/ }).click()
    await expect(page.getByText(`STEP ${i} OF 8`)).toBeVisible()
  }
  await page.getByRole('button', { name: /3D/ }).click()
  const part = page.locator('.flat-diagram').getByRole('button', { name: /Encoder/ })
  await part.focus()
  await page.keyboard.press('Enter')
  await expect(part).toHaveAttribute('aria-pressed', 'true')
})
