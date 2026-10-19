import { ArrowRight, CheckCircle, XCircle } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import type { Component, TokenOut, TokenizeResult } from '../../api/types'
import { showToken } from './adapter'

/**
 * "What goes in → what comes out" for one tokenizer stage, drawn from the last
 * REAL run. Every value is read from the experiment result; nothing is mocked.
 */
export function TokStageIO({ component, result }: { component: Component; result: TokenizeResult | null }) {
  const io = result ? views(component.id, result) : null
  return (
    <div className="stage-io" aria-label={`What goes into and comes out of ${component.label}`}>
      <IOCard title="Goes in" items={component.inputs ?? []}>{io?.input}</IOCard>
      <ArrowRight className="stage-io__arrow" aria-hidden />
      <IOCard title="Comes out" items={component.outputs ?? []}>{io?.output}</IOCard>
    </div>
  )
}

function IOCard({ title, items, children }: { title: string; items: string[]; children?: ReactNode }) {
  return (
    <section className="io-card">
      <h4 className="label">{title}</h4>
      <p className="io-card__what">{items.join(' + ') || '—'}</p>
      <div className="io-card__viz">{children ?? <span className="label">RUNNING…</span>}</div>
    </section>
  )
}

const Mono = ({ children }: { children: ReactNode }) => <code className="io-mono">{children}</code>

/** Small token chips; unknown and partial tokens are labelled, never colour alone. */
export function Chips({ items, max = 10, label }: { items: string[]; max?: number; label: string }) {
  return (
    <ol className="io-chips" aria-label={label}>
      {items.slice(0, max).map((t, i) => (
        <li key={i} className={`io-chip${t === '[UNK]' ? ' io-chip--unk' : ''}`}>
          {t === '[UNK]' ? '[UNK]' : showToken(t)}
        </li>
      ))}
      {items.length > max && <li className="label">+{items.length - max}</li>}
    </ol>
  )
}

const tokText = (t: TokenOut) => (t.is_unk ? '[UNK]' : t.text ?? t.bytes_hex)

function views(id: string, r: TokenizeResult): { input: ReactNode; output: ReactNode } {
  const t = r.training
  switch (id) {
    case 'corpus':
      return {
        input: <p className="io-quote">“{r.corpus.text.slice(0, 90)}…”</p>,
        output: <Mono>{r.corpus.characters} chars · {r.corpus.bytes} bytes</Mono>,
      }
    case 'pre_tokenizer':
      return {
        input: <Mono>{r.corpus.characters} chars of text</Mono>,
        output:
          r.pre_tokens.mode === 'words' ? (
            <>
              <Chips items={r.pre_tokens.sample.map((s) => s.text)} max={8} label="Most frequent word pieces" />
              <span className="label">{r.pre_tokens.count} PIECES · {r.pre_tokens.unique} DISTINCT</span>
            </>
          ) : (
            <Mono>no split: one long piece per text</Mono>
          ),
      }
    case 'base_alphabet':
      return {
        input: <Mono>{r.pre_tokens.unique} distinct pieces</Mono>,
        output: <Mono>{r.base.size} starting symbols · {r.base.mode === 'bytes' ? 'all 256 bytes' : 'characters seen + [UNK]'}</Mono>,
      }
    case 'merge_learner':
      return {
        input: <Mono>symbol sequences</Mono>,
        output: (
          <>
            <ol className="io-list" aria-label="First learned merges">
              {t.steps.slice(0, 4).map((s) => (
                <li key={s.rank}>
                  <code className="io-mono">
                    {showToken(s.left)} + {showToken(s.right)} → {showToken(s.token)}
                  </code>
                  <span className="io-list__score">×{s.count}</span>
                </li>
              ))}
            </ol>
            <span className="label">{t.merges_learned} MERGES LEARNED</span>
          </>
        ),
      }
    case 'vocabulary':
      return {
        input: <Mono>{r.vocabulary.merges} ordered merges</Mono>,
        output: (
          <Mono>
            {r.vocabulary.base_size} base + {r.vocabulary.merges} merges + {r.vocabulary.special.length} special = {r.vocabulary.size} ids
          </Mono>
        ),
      }
    case 'input_text':
      return {
        input: <p className="io-quote">“{r.input.text}”</p>,
        output: <Mono>{r.input.characters} chars · {r.input.bytes} bytes · {r.input.pieces} pieces</Mono>,
      }
    case 'encoder':
      return {
        input: <Mono>vocabulary + “{r.input.text.slice(0, 24)}{r.input.text.length > 24 ? '…' : ''}”</Mono>,
        output: (
          <>
            <Chips items={r.encoding.tokens.map(tokText)} label="Tokens" />
            <span className="label">{r.encoding.count} TOKEN IDS</span>
          </>
        ),
      }
    default:
      return {
        input: <Mono>{r.encoding.count} ids</Mono>,
        output: (
          <p className="outcome__answer">
            {r.decoding.round_trip ? <CheckCircle weight="fill" className="is-pass" aria-hidden /> : <XCircle weight="fill" className="is-fail" aria-hidden />}
            <span>
              {r.decoding.round_trip ? 'Round trip exact: ' : 'Round trip fails: '}“{r.decoding.text}”
            </span>
          </p>
        ),
      }
  }
}
