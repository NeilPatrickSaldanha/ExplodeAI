import { expect, test } from '@playwright/test'

const LESSONS = [
  { path: '/lessons/rag-pipeline', second: 'Warranty', expect: 'warranty#0' },
  { path: '/lessons/tokenization', second: 'Unseen words', expect: '18 tokens' },
  { path: '/lessons/embeddings', second: 'Bookshelf', expect: '0.695' },
  { path: '/lessons/attention', second: 'Pronoun', expect: 'about 28%' },
  { path: '/lessons/agents', second: 'Too late', expect: '50 days' },
]

for (const l of LESSONS) {
  test(`${l.path}: the Experiment tab says what to try and what you should see`, async ({ page }) => {
    await page.goto(l.path)
    await page.getByRole('tab', { name: 'Experiment', exact: true }).click()
    const guide = page.locator('.xguide')
    await expect(guide).toBeVisible()
    await expect(guide.locator('.xguide__intro')).not.toBeEmpty()
    await page.locator('.presets').getByRole('button', { name: l.second }).click()
    await expect(guide.locator('.xguide__preset')).toContainText('YOU SHOULD SEE')
    await expect(guide.locator('.xguide__preset')).toContainText(l.expect)
    // Other ideas stay folded away until asked for.
    await expect(guide.locator('.xguide__ideas')).not.toHaveAttribute('open', '')
    await guide.locator('.xguide__ideas summary').click()
    expect(await guide.locator('.xguide__ideas li').count()).toBeGreaterThanOrEqual(3)
    // The open result tab explains itself in one sentence.
    await expect(page.locator('.rtabs__panel[data-state="active"] .tabhint').first()).toContainText('IN THIS TAB')
  })
}

test('with no example picked, the guide points at the example buttons', async ({ page }) => {
  await page.goto('/lessons/embeddings')
  await page.getByRole('tab', { name: 'Experiment', exact: true }).click()
  await page.getByLabel('Your text').fill('my own sentence about trains')
  await expect(page.locator('.xguide__hint')).toContainText('example buttons')
})

test('the guide is hidden while a Break & fix challenge locks the input', async ({ page }) => {
  await page.goto('/lessons/embeddings')
  await page.getByRole('tab', { name: 'Break & fix', exact: true }).click()
  await page.getByRole('button', { name: /Same meaning, no shared words/ }).click()
  await expect(page.locator('.xguide')).toHaveCount(0)
})
