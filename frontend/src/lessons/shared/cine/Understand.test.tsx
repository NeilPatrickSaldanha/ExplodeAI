import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { Component, Explain } from '../../../api/types'
import { Understand } from './Understand'
import { rememberTutorial, tutorialSeen, TUTORIAL_KEY } from './tutorialStorage'

const comp = (id: string, label: string) => ({ id, label }) as Component
const explain: Explain = {
  what: 'Turns text into numbers.',
  why: 'Computers compare numbers.',
  analogy: 'A map coordinate.',
  happens: ['Text goes in', 'Numbers come out'],
  goes_to: 'The next stage.',
  example: { input: 'cat', steps: ['split', 'encode'], output: '[0.1, 0.2]' },
  misconfigured: 'Wrong model, wrong answer.',
  learn_more: 'Technical depth.',
  claims: ['a', 'b'],
}

function setup(reducedMotion = false) {
  const onGoTo = vi.fn()
  render(<Understand component={comp('x', 'X')} explain={explain} before={[comp('p', 'Prev')]} after={[comp('n', 'Next')]} reducedMotion={reducedMotion} onGoTo={onGoTo} />)
  return onGoTo
}

describe('Understand', () => {
  it('shows the short version first and keeps the depth collapsed', () => {
    setup()
    expect(screen.getByText('Turns text into numbers.')).toBeInTheDocument()
    expect(screen.getByText(/ANALOGY/)).toBeInTheDocument()
    const why = screen.getByText('Why it is needed').closest('details')!
    expect(why.open).toBe(false)
    fireEvent.click(screen.getByText('Why it is needed'))
    expect(screen.getByText('Computers compare numbers.')).toBeInTheDocument()
  })

  it('links to the stages before and after', () => {
    const onGoTo = setup()
    fireEvent.click(screen.getByRole('button', { name: /to Next/ }))
    fireEvent.click(screen.getByRole('button', { name: /from Prev/ }))
    expect(onGoTo.mock.calls).toEqual([['n'], ['p']])
  })

  it('steps through the example one step at a time', () => {
    setup()
    const on = () => document.querySelectorAll('.demo__steps li.is-on').length
    expect(on()).toBe(0)
    fireEvent.click(screen.getByRole('button', { name: /Step/ }))
    expect(on()).toBe(1)
    fireEvent.click(screen.getByRole('button', { name: /Step/ }))
    fireEvent.click(screen.getByRole('button', { name: /Step/ }))
    expect(document.querySelectorAll('.demo__card.is-on').length).toBe(2)
  })

  it('shows the whole example at once when motion is reduced', () => {
    setup(true)
    expect(document.querySelectorAll('.demo__steps li.is-on').length).toBe(2)
  })
})

describe('tutorial memory', () => {
  const store = new Map<string, string>()
  const fake = {
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => void store.set(k, v),
  }

  it('remembers a finished or skipped tutorial, and never nags when storage is blocked', () => {
    vi.stubGlobal('localStorage', fake)
    expect(tutorialSeen()).toBe(false)
    rememberTutorial('skipped')
    expect(store.get(TUTORIAL_KEY)).toBe('skipped')
    expect(tutorialSeen()).toBe(true)
    vi.stubGlobal('localStorage', {
      getItem: () => {
        throw new Error('blocked')
      },
    })
    expect(tutorialSeen()).toBe(true)
    vi.unstubAllGlobals()
  })
})
