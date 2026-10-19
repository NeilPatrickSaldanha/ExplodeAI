import { act, fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { TokenizeResult } from '../../api/types'
import { readoutsFromResult, replayEvents, segmentationAt, showToken } from './adapter'
import fixture from './fixture.json'
import { MergeReplay, MergeTable, TokenStrip, TradeoffChart } from './TokenViews'

// A real backend run (text "The keeper lit the lantern. Café", 40 merges), trimmed.
const result = fixture as unknown as TokenizeResult

describe('adapter', () => {
  it('shows spaces inside tokens', () => {
    expect(showToken(' keeper')).toBe('·keeper')
    expect(showToken('a\nb')).toBe('a↵b')
  })

  it('readouts come from the real run', () => {
    const r = readoutsFromResult(result)!
    expect(r.parts!.base_alphabet).toBe('256 SYMBOLS · BYTES')
    expect(r.parts!.encoder).toBe(`${result.encoding.count} TOKENS`)
    expect(r.parts!.decoder).toBe('ROUND TRIP EXACT')
    expect(r.links!['encoder->decoder']).toBe(`${result.encoding.count} ids`)
  })

  it('replaying every event reproduces the final tokens, in learned order', () => {
    const events = replayEvents(result)
    expect(events.map((e) => e.rank)).toEqual([...events.map((e) => e.rank)].sort((a, b) => a - b))
    const final = segmentationAt(result, events, events.length).flat()
    const tokens = result.encoding.tokens.map((t) => t.text ?? t.bytes_hex)
    expect(final).toEqual(tokens)
    expect(segmentationAt(result, events, 0).flat().length).toBe(result.input.bytes)
  })
})

describe('token views', () => {
  it('labels a token that holds part of a character instead of hiding it', () => {
    render(<TokenStrip result={result} />)
    expect(screen.getAllByText('PARTIAL')).toHaveLength(2)
    expect(screen.getByRole('status')).toHaveTextContent('Round trip exact')
  })

  it('flags unknown tokens and a failed round trip with text, not colour alone', () => {
    const broken: TokenizeResult = {
      ...result,
      encoding: { ...result.encoding, tokens: [{ id: 0, text: '[UNK]', bytes_hex: '', is_unk: true }] },
      decoding: { text: '�', round_trip: false, unk_count: 1 },
    }
    render(<TokenStrip result={broken} />)
    expect(screen.getByText('UNKNOWN')).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('Round trip fails')
  })

  it('lists merges with the vocabulary formula', () => {
    render(<MergeTable result={result} />)
    const v = result.vocabulary
    expect(screen.getByText(new RegExp(`${v.base_size} BASE \\+ ${v.merges} MERGES \\+ 1 SPECIAL = ${v.size}`))).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Learned merges in order' })).toBeInTheDocument()
  })

  it('replay steps with buttons and hides autoplay under reduced motion', () => {
    render(<MergeReplay result={result} reducedMotion />)
    expect(screen.queryByRole('button', { name: 'Play replay' })).not.toBeInTheDocument()
    expect(screen.getByText(/AUTOPLAY OFF/)).toBeInTheDocument()
    const prev = screen.getByRole('button', { name: 'Previous merge' })
    act(() => fireEvent.click(prev))
    expect(screen.getByText(/^Step \d+: merge rank/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Next merge' })).not.toBeDisabled()
  })

  it('offers autoplay when motion is allowed', () => {
    render(<MergeReplay result={result} reducedMotion={false} />)
    expect(screen.getByRole('button', { name: 'Play replay' })).toBeInTheDocument()
  })

  it('trade-off chart has a text alternative and marks your setting', () => {
    render(<TradeoffChart result={result} />)
    expect(screen.getByRole('img', { name: /Line chart: as the vocabulary grows/ })).toBeInTheDocument()
    const table = screen.getByRole('region', { name: 'Trade-off data' })
    expect(table).toHaveTextContent('40 (yours)')
    expect(screen.getByText(/YOUR SETTING · 40 MERGES/)).toBeInTheDocument()
  })
})
