import { expect, test, type Page } from '@playwright/test'

const LESSON = '/lessons/agents'
const panel = (page: Page) => page.locator('.cine__panel')
const stages = (page: Page) => page.getByRole('navigation', { name: 'Pipeline stages' })
const openMode = (page: Page, name: string) => page.getByRole('tab', { name, exact: true }).click()
const seg = (page: Page, group: string, option: string) => page.getByRole('group', { name: group }).getByRole('radio', { name: option, exact: true })
const trace = (page: Page) => page.locator('.atrace')

test('home lists lesson 05 and it opens with its 3D scene and cited stages', async ({ page }) => {
  await page.goto('/')
  const link = page.getByRole('link', { name: /tool-using agents, exploded/i })
  await expect(link).toContainText('05 ·')
  await link.click()
  await expect(page).toHaveURL(new RegExp(`${LESSON}$`))
  await expect(page.locator('.exploded-view[data-mode="3d"] canvas')).toBeVisible()
  await stages(page).getByRole('button', { name: /Tool registry/ }).click()
  await expect(panel(page).getByRole('heading', { name: 'Tool registry' })).toBeVisible()
  await expect(panel(page).getByText('STAGE 02 / 08')).toBeVisible()
  await panel(page).locator('.fact__head').first().click()
  await expect(panel(page).locator('a.claim__source').first()).toHaveAttribute('href', /^https?:\/\//)
})

test('experiment: a real loop, labelled, that rejects a bad ID, fixes it and waits for a person', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await expect(page.getByText('REAL EXECUTION · THE LOOP AND ITS TOOLS')).toBeVisible()
  await expect(page.getByText('SIMULATION · STAND-IN DECIDER')).toBeVisible()
  await expect(panel(page).getByRole('note')).toContainText('not a language model')
  await expect(trace(page).locator('.atrace__step')).toHaveCount(5)
  await expect(trace(page)).toContainText("Rejected: 'order_id' must match")
  await expect(trace(page)).toContainText('Not run: waiting for a person to approve')
  await expect(panel(page).getByRole('heading', { name: /wants to move money/ })).toBeVisible()
  await panel(page).getByRole('button', { name: 'Approve this refund' }).click()
  await expect(trace(page).locator('.atrace__status')).toContainText('Answered')
  await expect(trace(page).locator('.atrace__answer')).toContainText('16 days ago')
  await expect(trace(page).locator('.atrace__answer')).toContainText('Refund R-001')
})

test('switching a setting takes back an approval', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await panel(page).getByRole('button', { name: 'Approve this refund' }).click()
  await expect(trace(page).locator('.atrace__status')).toContainText('Answered')
  await seg(page, 'Tool descriptions', 'Vague').click()
  await expect(trace(page).locator('.atrace__status')).not.toContainText('Answered')
})

test('with argument checking off, the bad ID reaches the tool and the agent says the order does not exist', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await seg(page, 'Check arguments before running', 'Off').click()
  await expect(trace(page)).toContainText('Arguments are not checked')
  await expect(trace(page).locator('.atrace__answer')).toContainText("couldn't find an order called 1001")
})

test('vague descriptions with no step limit run until the safety cap, and the token cost shows it', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await seg(page, 'Tool descriptions', 'Vague').click()
  await seg(page, 'Step limit', 'None').click()
  await expect(trace(page).locator('.atrace__status')).toContainText('safety cap')
  await expect(trace(page).locator('.atrace__step')).toHaveCount(30)
  await page.getByRole('tab', { name: 'Token cost' }).click()
  await expect(panel(page).locator('.actx__sum')).toContainText('in 30 steps')
})

test('the model reads the whole conversation again each step', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Experiment')
  await page.getByRole('tab', { name: 'What the model reads' }).click()
  const conv = panel(page).locator('.aconv')
  await expect(conv).toContainText('Every step re-sends all of it')
  await expect(conv.locator('.aconv__msg').first()).toContainText('System')
  await expect(conv).toContainText('Result · get_order')
})

test('what breaks if removed: without argument checks the loop really reports a missing order', async ({ page }) => {
  await page.goto(LESSON)
  await stages(page).getByRole('button', { name: /Check/ }).click()
  await panel(page).getByRole('button', { name: 'Run without the check' }).click()
  const compare = panel(page).locator('.breaks__compare')
  await expect(compare).toContainText('Real execution, part removed')
  await expect(compare).toContainText("I couldn't find an order called 1001")
})

test('break & fix: step limit, detailed descriptions and approval each fix their own challenge', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Break & fix')
  await page.getByRole('button', { name: /The agent that never stops/ }).click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Still broken.')
  await seg(page, 'Step limit', '8').click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Fixed.')
  await page.getByRole('button', { name: '← All challenges' }).click()

  await page.getByRole('button', { name: /The tool that was never chosen/ }).click()
  await expect(seg(page, 'Tool descriptions', 'Vague')).toHaveAttribute('aria-checked', 'true')
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Still broken.')
  await seg(page, 'Tool descriptions', 'Detailed').click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Fixed.')
  await page.getByRole('button', { name: '← All challenges' }).click()

  await page.getByRole('button', { name: /The refund nobody approved/ }).click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Still broken.')
  await seg(page, 'Person approves refunds', 'On').click()
  await page.getByRole('button', { name: 'Check my fix' }).click()
  await expect(page.locator('.challenges .check')).toContainText('Fixed.')
})

test('the tour reaches all eight steps', async ({ page }) => {
  await page.goto(LESSON)
  await openMode(page, 'Tour')
  for (let i = 2; i <= 8; i++) {
    await panel(page).getByRole('button', { name: 'Next stage' }).click()
    await expect(page.getByText(`TOUR · STEP ${i} OF 8`)).toBeVisible()
  }
})
