import * as RSlider from '@radix-ui/react-slider'
import * as ToggleGroup from '@radix-ui/react-toggle-group'
import { Cube, Flask, LockSimple, PencilRuler } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import type { Visual } from '../api/types'

const KIND_META: Record<Visual['kind'], { icon: ReactNode; text: string }> = {
  real_execution: { icon: <Flask weight="bold" aria-hidden />, text: 'Real execution' },
  simulation: { icon: <Cube weight="bold" aria-hidden />, text: 'Simulation' },
  conceptual: { icon: <PencilRuler weight="bold" aria-hidden />, text: 'Conceptual' },
}

/** Every visual says what it is. Icon + text, never colour alone. */
export function KindBadge({ visual }: { visual: Visual }) {
  const meta = KIND_META[visual.kind]
  return (
    <span className={`kind-badge kind-badge--${visual.kind}`} title={visual.description}>
      {meta.icon}
      <span>{visual.label || meta.text}</span>
    </span>
  )
}

interface SliderProps {
  id: string
  label: string
  value: number
  min: number
  max: number
  step?: number
  unit?: string
  disabled?: boolean
  onChange: (v: number) => void
  format?: (v: number) => string
}

export function Slider({ id, label, value, min, max, step = 1, unit, disabled, onChange, format }: SliderProps) {
  const shown = format ? format(value) : `${value}${unit ? ` ${unit}` : ''}`
  return (
    <div className={`field${disabled ? ' is-locked' : ''}`}>
      <div className="field__head">
        <label className="label" id={`${id}-label`} htmlFor={id}>
          {label}
          {disabled && <LockSimple aria-label="locked" weight="bold" className="field__lock" />}
        </label>
        <output className="field__value" htmlFor={id}>
          {shown}
        </output>
      </div>
      <RSlider.Root
        className="slider"
        value={[value]}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        onValueChange={([v]) => onChange(v)}
        aria-labelledby={`${id}-label`}
      >
        <RSlider.Track className="slider__track">
          <RSlider.Range className="slider__range" />
        </RSlider.Track>
        <RSlider.Thumb className="slider__thumb" id={id} aria-label={label} aria-valuetext={shown} />
      </RSlider.Root>
    </div>
  )
}

interface SegmentedProps<T extends string> {
  label: string
  value: T
  options: { value: T; label: string; disabled?: boolean }[]
  onChange: (v: T) => void
  disabled?: boolean
}

export function Segmented<T extends string>({ label, value, options, onChange, disabled }: SegmentedProps<T>) {
  return (
    <div className={`field${disabled ? ' is-locked' : ''}`} role="group" aria-label={label}>
      <span className="label">
        {label}
        {disabled && <LockSimple aria-label="locked" weight="bold" className="field__lock" />}
      </span>
      <ToggleGroup.Root
        type="single"
        className="segmented"
        value={value}
        onValueChange={(v) => v && onChange(v as T)}
        disabled={disabled}
        aria-label={label}
      >
        {options.map((o) => (
          <ToggleGroup.Item key={o.value} value={o.value} className="segmented__item" disabled={o.disabled}>
            {o.label}
          </ToggleGroup.Item>
        ))}
      </ToggleGroup.Root>
    </div>
  )
}

export function Toggle({ pressed, onChange, children, label }: { pressed: boolean; onChange: (v: boolean) => void; children: ReactNode; label: string }) {
  return (
    <button type="button" className="btn btn--toggle" aria-pressed={pressed} onClick={() => onChange(!pressed)} title={label}>
      {children}
    </button>
  )
}
