# Mobile checklist

What is automated, and what needs a real phone.

## Automated (every run)

- `frontend/e2e/responsive.spec.ts` checks all four lessons at 320, 375, 430 px, phone landscape (844×390) and
  tablet (768): no sideways scrolling, no control clipped off the right edge, all five modes reachable, and the
  tutor keeping room for its conversation, suggestion chips and input.
- `frontend/e2e/mobile.spec.ts` (Pixel 7 emulation) checks touch target sizes, the tutorial as a bottom sheet,
  stage explanations and the tutor on a phone.
- Layout rules that matter on phones live in `cine.css` (the `.spanel` grid uses `minmax(0, 1fr)` so a long word
  cannot widen the column; the five modes wrap on small screens), `tutor.css` (icon-only button, one scrolling
  row of chips, compact layout on short screens) and `app.css` (long source titles wrap).

## Needs your real phone (emulators cannot judge these)

1. **Dragging the 3D model.** Drag it with one finger: does it rotate, or does the page scroll instead? Pinch to
   zoom. If dragging fights the page scroll, tell me which direction misbehaves.
2. **On-screen keyboard.** Open **Ask ExplodeAI** and tap the question box. Can you still see the box and the
   last answer with the keyboard open?
3. **Tutorial spotlight.** Clear site data (or use a private tab), open a lesson, and run the first-time
   tutorial. Does each highlighted control stay in view, and are Next and Skip easy to hit?
4. **Thumb reach.** Is the floating chat button comfortable to reach and does it cover anything you need?
5. **Rotate to landscape** on a lesson and in the tutor.
6. **Small or older phones**, if you have one (320–360 px wide).
7. **Dark and light mode** on the phone, outdoors in sunlight if you can: is the contrast readable?
8. **Slow network.** Throttle or move away from Wi-Fi: does the first load (the 3D scene) show something sensible?

Report anything odd as "device, browser, lesson, what you did, what you saw" and a screenshot.
