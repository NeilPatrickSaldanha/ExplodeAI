import { expect, test, type Page } from '@playwright/test'

const stages = (page: Page) => page.getByRole('navigation', { name: 'Pipeline stages' })
const panel = (page: Page) => page.locator('.tutor')

async function openTutor(page: Page) {
  // The tutor remembers being open for the browser session, so only click when it is closed.
  const fab = page.getByRole('button', { name: 'Ask ExplodeAI' })
  await expect(fab).toBeVisible()
  if ((await fab.getAttribute('aria-expanded')) !== 'true') await fab.click()
  await expect(panel(page)).toBeVisible()
}
async function ask(page: Page, q: string) {
  await page.getByLabel('Your question').fill(q)
  await page.getByRole('button', { name: 'Ask', exact: true }).click()
}

test('asking gives a cited answer from the lessons, with evidence and a link to the stage', async ({ page }) => {
  await page.goto('/lessons/attention')
  await openTutor(page)
  await ask(page, 'Why do we divide the scores by the square root of d_k?')
  const answer = panel(page).locator('.tmsg--tutor').last()
  await expect(answer.locator('.tmsg__body p').first()).toContainText('√d_k')
  await expect(answer.locator('.tmsg__cite').first()).toContainText('attn-')
  await answer.getByText(/^Evidence:/).click()
  await expect(answer.locator('.tmsg__sources a').first()).toHaveAttribute('href', /^https?:\/\//)
  await answer.getByRole('button', { name: /Show me: Score grid/ }).click()
  await expect(page.locator('.cine__panel').getByRole('heading', { name: 'Score grid' })).toBeVisible()
})

test('a question the lessons do not cover is refused, with no sources and a way forward', async ({ page }) => {
  await page.goto('/lessons/embeddings')
  await openTutor(page)
  await ask(page, 'Who won the world cup?')
  const msg = panel(page).locator('.tmsg--none')
  await expect(msg).toContainText("don't cover that")
  await expect(msg.getByRole('link')).toHaveCount(4)
  await expect(panel(page).locator('.tmsg__evidence')).toHaveCount(0)
})

test('the tutor knows which stage is open, and tutor mode quizzes on it', async ({ page }) => {
  await page.goto('/lessons/attention')
  await stages(page).getByRole('button', { name: /Softmax/ }).click()
  await openTutor(page)
  await expect(page.getByTestId('tutor-context')).toContainText('SOFTMAX')
  await expect(panel(page).getByRole('button', { name: 'What happens if Softmax is removed?' })).toBeVisible()
  await panel(page).getByRole('button', { name: /Quiz me on Softmax/ }).click()
  const quiz = panel(page).locator('.tmsg--quiz')
  await expect(quiz).toContainText('QUIZ · SOFTMAX · 1 OF 5')
  await expect(quiz).not.toContainText('Raw scores are used as weights')
  await quiz.getByRole('button', { name: 'Show the answer' }).click()
  await expect(quiz.locator('.tmsg__a')).toContainText('Attention weights')
  await quiz.getByRole('button', { name: 'Next question' }).click()
  await expect(panel(page).locator('.tmsg--quiz').last()).toContainText('2 OF 5')
  // Changing stage changes the context.
  await stages(page).getByRole('button', { name: /Mask/ }).click()
  await expect(page.getByTestId('tutor-context')).toContainText('MASK')
})

test('keyboard: Escape closes the tutor and returns focus to its button', async ({ page }) => {
  await page.goto('/lessons/tokenization')
  await openTutor(page)
  await page.getByLabel('Your question').focus()
  await page.keyboard.press('Escape')
  await expect(panel(page)).toBeHidden()
  await expect(page.getByRole('button', { name: 'Ask ExplodeAI' })).toBeFocused()
  await expect(page.getByRole('button', { name: 'Ask ExplodeAI' })).toHaveAttribute('aria-expanded', 'false')
})

test('the optional paid polish is clearly off when the server has no AI enabled', async ({ page }) => {
  await page.goto('/lessons/rag-pipeline')
  await openTutor(page)
  await ask(page, 'What is BM25?')
  const answer = panel(page).locator('.tmsg--tutor').last()
  await answer.getByRole('button', { name: /Re-explain this with AI/ }).click()
  await expect(answer).toContainText('AI is off on this server')
})

test('every lesson has the tutor button, and the page never scrolls sideways with it open', async ({ page }) => {
  for (const l of ['rag-pipeline', 'tokenization', 'embeddings', 'attention']) {
    await page.goto(`/lessons/${l}`)
    await openTutor(page)
    await expect(panel(page)).toContainText('Answers come only from')
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
    expect(overflow).toBeLessThanOrEqual(0)
  }
})

test('small talk gets a friendly reply, not a refusal', async ({ page }) => {
  await page.goto('/lessons/attention')
  await openTutor(page)
  await ask(page, 'hi there')
  const reply = panel(page).locator('.tmsg--chat')
  await expect(reply).toContainText("I'm the ExplodeAI tutor")
  await expect(panel(page)).not.toContainText("don't cover that")
})

test('answers lead with plain words, and follow-ups like "easier words" remember the topic', async ({ page }) => {
  await page.goto('/lessons/attention')
  await openTutor(page)
  await ask(page, 'wait so what does vectors + position do?')
  const first = panel(page).locator('.tmsg--tutor').last()
  await expect(first.locator('.tplain')).toContainText('IN PLAIN WORDS · VECTORS + POSITION')
  await expect(first.locator('.tplain__what')).toContainText('vector of 64 numbers')
  await expect(first.locator('.tmsg__body')).toContainText('FROM THE LESSONS · VERIFIED')
  // The follow-up has no topic of its own: it must be about the same stage.
  await ask(page, 'can you frame it in easier words')
  const second = panel(page).locator('.tmsg--tutor').last()
  await expect(second.locator('.tplain')).toContainText('VECTORS + POSITION')
  await expect(second.locator('.tmsg__analogy')).toContainText('THINK OF IT LIKE')
  await expect(second.locator('.tplain__example')).toContainText('EXAMPLE · ILLUSTRATIVE')
  await expect(panel(page)).not.toContainText("don't cover that")
  await ask(page, 'give me an example')
  await expect(panel(page).locator('.tplain__example').last()).toContainText('dog')
})

test('with a stage open, "explain it simpler" is about that stage', async ({ page }) => {
  await page.goto('/lessons/tokenization')
  await stages(page).getByRole('button', { name: /Merge learner/ }).click()
  await openTutor(page)
  await ask(page, 'explain it simpler')
  await expect(panel(page).locator('.tplain').last()).toContainText('MERGE LEARNER')
})

test('the AI explain switch is clearly off when the server has AI disabled', async ({ page }) => {
  await page.goto('/lessons/embeddings')
  await openTutor(page)
  await expect(panel(page).locator('.tutor__ai--off')).toContainText('Explain with AI: off on this server')
  await expect(panel(page).getByRole('checkbox')).toHaveCount(0)
})
