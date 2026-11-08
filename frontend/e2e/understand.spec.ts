import { expect, test } from '@playwright/test'

const LESSONS = [
  { path: '/lessons/rag-pipeline', stage: /Chunker/, heading: 'Chunker' },
  { path: '/lessons/tokenization', stage: /Merge learner/, heading: 'Merge learner' },
  { path: '/lessons/embeddings', stage: /Encoder/, heading: 'Encoder' },
]

for (const l of LESSONS) {
  test(`${l.heading}: deeper explanation opens progressively and links to neighbours`, async ({ page }) => {
    await page.goto(l.path)
    await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: l.stage }).click()
    const u = page.locator('.cine__panel .understand')
    await expect(u).toBeVisible()
    // Short version is visible; depth is collapsed until asked for.
    await expect(u.locator('.understand__analogy')).toContainText('THINK OF IT LIKE')
    await expect(u.locator('.understand__story')).not.toBeEmpty()
    await expect(u.locator('.understand__thread')).toContainText('IN OUR EXAMPLE')
    await expect(u.locator('.demo')).toContainText('ILLUSTRATIVE EXAMPLE')
    const why = u.locator('details', { hasText: 'Why it is needed' })
    await expect(why).not.toHaveAttribute('open', '')
    await why.locator('summary').click()
    await expect(why).toHaveAttribute('open', '')
    // Technical depth sits behind its own toggle and points at the verified claims.
    const more = u.locator('details', { hasText: 'Learn more (technical)' })
    await more.locator('summary').click()
    await expect(more).toContainText(/VERIFIED CLAIM/)
    // Connected stages are clickable and move the whole lesson.
    const nextChip = u.locator('.handoff .chip', { hasText: /^to / }).first()
    const target = (await nextChip.textContent())!.replace(/^to /, '').replace(/ →$/, '')
    await nextChip.click()
    await expect(page.locator('.cine__panel .spanel__title')).toHaveText(new RegExp(target, 'i'))
  })
}

test('the example demo steps through input, steps and output', async ({ page }) => {
  await page.goto('/lessons/embeddings')
  await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: /Pooling/ }).click()
  const demo = page.locator('.cine__panel .demo')
  await expect(demo.locator('.demo__card.is-on')).toHaveCount(1) // only the input shows at first
  await demo.getByRole('button', { name: 'Step' }).click()
  await expect(demo.locator('.demo__steps li.is-on')).toHaveCount(1)
  await demo.getByRole('button', { name: 'Step' }).click()
  await demo.getByRole('button', { name: 'Step' }).click()
  await expect(demo.locator('.demo__card.is-on')).toHaveCount(2) // input and output
})

test('Calm mode shows the whole example at once, with no timed animation', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/lessons/embeddings')
  await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: /Pooling/ }).click()
  await expect(page.locator('.cine__panel .demo__card.is-on')).toHaveCount(2)
})


test('the check-yourself question hides its answer until you ask', async ({ page }) => {
  await page.goto('/lessons/rag-pipeline')
  await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: /Retriever/ }).click()
  const check = page.locator('.cine__panel .check-yourself')
  await expect(check.locator('.check-yourself__q')).toContainText('top few chunks')
  await expect(check.locator('.check-yourself__a')).toHaveCount(0)
  await check.getByRole('button', { name: /show the answer/i }).click()
  await expect(check.locator('.check-yourself__a')).toContainText('limited size')
})

test('every hand-off is explained in a full sentence', async ({ page }) => {
  await page.goto('/lessons/tokenization')
  await page.getByRole('navigation', { name: 'Pipeline stages' }).getByRole('button', { name: /Encoder/ }).click()
  const hand = page.locator('.cine__panel .handoff')
  await expect(hand).toHaveCount(3) // from the vocabulary, from the input text, to the decoder
  for (const p of await hand.locator('p').allTextContents()) expect(p.length).toBeGreaterThan(40)
})

test('the big picture opens every lesson, maps stages to an analogy, and remembers being closed', async ({ page }) => {
  await page.goto('/lessons/attention')
  const card = page.locator('.bigpic')
  await expect(card).toHaveAttribute('open', '')
  await expect(card.locator('.bigpic__map li')).toHaveCount(8)
  await expect(card.locator('.bigpic__breaks')).toContainText('toy')
  await card.getByRole('button', { name: 'Softmax' }).click()
  await expect(page.locator('.cine__panel .spanel__title')).toHaveText(/softmax/i)
  await card.locator('summary').click()
  await expect(card).not.toHaveAttribute('open', '')
  await page.waitForFunction(() => localStorage.getItem('explodeai.bigpicture.attention') === 'closed')
  await page.reload()
  await expect(page.locator('.bigpic')).not.toHaveAttribute('open', '')
})
