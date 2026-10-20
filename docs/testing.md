# Testing strategy

| Layer | Tool | Where | What it proves |
|---|---|---|---|
| Content gate | validator script | `backend/scripts/validate_content.py` | citations, sources, verification passes, references |
| Backend unit | pytest | `backend/tests/test_rag_stages.py`, `test_tokenize.py`, `test_embed.py`, `test_embed_ablation.py` | each pipeline stage, plus Pass 3 claim evidence (tokenization: an independent reference BPE, merge-order, prefix, round-trip properties over random mixed-script text) |
| Backend integration | pytest + TestClient | `test_api.py`, `test_pipeline_and_content.py` | API behaviour, draft gating, locked challenge params, progress merge, model ↔ pipeline consistency, validator negatives |
| Paid-AI safety | pytest + `httpx.MockTransport` | `test_ai_guard.py` | every refusal path, kill switch precedence, budgets, rate limits, keys only in headers, no key echo — **no network** |
| Neural evidence | pytest (needs `--extra neural`) | `test_neural.py` | semantic-similarity claims with a real local model |
| Claim coverage | pytest | `test_zz_claim_coverage.py` | for every lesson: claim ids are unique, and every claim marked technically passed had a passing test this run |
| Frontend unit | Vitest + Testing Library | `frontend/src/**/*.test.tsx` | engine math, 2D fallback keyboard use, readouts, result views, rebuild helpers |
| End-to-end | Playwright (Chromium) | `frontend/e2e/` (`lesson.spec.ts`, `tokenization.spec.ts`, `embeddings.spec.ts`, `mobile.spec.ts`) | real 3D rendering, keyboard selection, real experiment, full break/fix loop with persistence, rebuild via buttons, 2D + reduced motion, tour, phone layout without horizontal scroll — for all three lessons |

E2E starts its own backend (isolated SQLite file, AI disabled) and frontend on
ports 8100 and 5174, so it never touches development data.

```bash
make test           # everything
make test-backend   # 185 tests (needs: uv sync --extra neural)
make test-frontend  # typecheck + 25 unit tests
make e2e            # 29 browser tests (E2E_API_PORT / E2E_WEB_PORT to move ports)
```
