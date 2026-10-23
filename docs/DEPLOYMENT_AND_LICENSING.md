# Deploying ExplodeAI publicly, and licensing

Written 2026-10-22. **Facts are marked by how well they are verified:** *measured* (I ran it), *repo* (read from the code), *official* (read on the provider's own page today), *secondary* (a blog or comparison page: check before relying on it), *unverified*. This is engineering guidance, not legal advice.

## 1. What the app needs to run (measured and from the repo)

| Item | Finding |
|---|---|
| Frontend | A static site. `npm run build` produced a **1.6 MB** `dist/` (main script about 435 kB gzipped; the 3D code is split into lazy chunks). *measured* |
| Backend | FastAPI app (Python 3.12) serving `/api/...`. It reads `content/` YAML at start. *repo* |
| Memory | About **14 MB idle** and about **276 MB** after the neural model and tutor had loaded and a few requests ran. Peak under load was not measured. *measured* |
| Neural model | The local embedding model (about the size of a small ONNX file) is downloaded on first use unless baked into the image. The existing `backend/Dockerfile` already installs the `neural` extra and sets `FASTEMBED_CACHE_PATH`. *repo* |
| Database | SQLite file for progress, run history and the AI ledger. On free hosts the disk is usually **ephemeral**, so progress would reset when the app restarts. Lessons themselves live in `content/` and are unaffected. *repo, official (Render, Hugging Face)* |
| Keys | **None needed.** With no keys the paid features stay disabled. *repo* |

### The one thing that blocks a public launch today
The frontend calls relative paths like `/api/lessons`, so the site and API must appear under **the same web address**. In development Vite proxies `/api` to port 8000. For production, nothing serves the built site: the backend doesn't serve static files, and `frontend/Dockerfile` runs the *development* server. *repo*

Two ways to fix it:

- **Option A (recommended): one container, one URL.** Have the FastAPI app also serve `frontend/dist` (a static-files mount plus a fallback to `index.html` for routes like `/lessons/agents`), and add a production Docker build that runs `npm run build` and copies `dist` in. Then there is a single service, no CORS setup, no second host, and one link to share on LinkedIn, which is what you want. This is a small code change (I have not made it).
- **Option B: static host + separate API.** Host `dist` on a static host and the API elsewhere. This needs either a rewrite/proxy of `/api` to the API host or a code change so the frontend reads an API base URL. More moving parts and two services to keep alive.

## 2. Free hosting options (checked 2026-10-22)

Free tiers change often. Re-check the official page the day you deploy.

| Host | What I found | Fit |
|---|---|---|
| **Hugging Face Spaces (Docker)** | Official docs describe Docker Spaces for "FastAPI and Go endpoints", the app listens on port **7860** by default, secrets are set in Space Settings, and **disk is lost on restart**. *official.* The free "CPU Basic" is listed as 2 vCPU and 16 GB RAM, and free hardware sleeps when idle (one library page says 48 hours). *official but the sleep time is not confirmed on one page.* **Unconfirmed:** one search snippet said creating a Docker Space needs a paid plan; the official Docker Spaces page does not say so. Check on the New Space page. | Best resource fit (lots of RAM, Docker, free, no 15-minute sleep) **if** the free account can create a Docker Space. |
| **Render (free web service)** | Official: spins down after **15 minutes** of no traffic and takes **about a minute** to wake; **750 free hours** per month; **ephemeral filesystem**; outbound bandwidth counts against a monthly included amount. The page does **not** state RAM/CPU, Docker support or commercial-use terms; secondary sites say 512 MB RAM, which would be tight with the neural model. *official + secondary* | Works for one container but the one-minute cold start is a poor first impression, and 512 MB (if true) is risky. |
| **Oracle Cloud Always Free** | Secondary sources describe a large always-free allowance (including ARM VMs with up to 24 GB RAM). You manage the server yourself, and the ARM VMs need arm64 images. *secondary* | Most capacity, most work (server setup, security updates, HTTPS). |
| **Fly.io** | Secondary sources say it no longer has a true free tier for new accounts. *secondary* | Probably not free. |
| **Cloudflare Pages** | Static hosting with generous free limits per secondary sources. It cannot run the Python backend. *secondary* | Only useful for Option B's frontend. |

**My recommendation:** build Option A, then try a **Hugging Face Docker Space** first and **Render free** as the fallback. Whichever you pick, add a custom domain later if you want a stable URL, and **open the site yourself a few minutes before each post** so a sleeping app is awake when LinkedIn traffic arrives. Cold starts cannot be eliminated on free tiers.

## 3. Production configuration checklist (from the repo)
- **Never copy `backend/.env` to the host.** Locally it enables paid AI features and holds keys. For a public site set no keys, and keep `AI_FEATURES_ENABLED=false` (the kill switch `AI_EMERGENCY_DISABLE=true` is also available). Visitors then cannot spend your money. If you ever enable paid answers, the existing guard caps spend ($4 lifetime in your config), but a public site makes that cap reachable by strangers, so keep it off.
- `SHOW_DRAFT_LESSONS` must stay `false` (the default).
- `DATABASE_URL` should point at a writable path. Expect progress to reset on restart on free tiers. `CORS_ORIGINS` is only needed for Option B.
- Bake the embedding model into the image at build time so the first visitor doesn't wait for a download.
- The per-visitor experiment rate limiter exists (`experiment_limiter`) but was designed for local use; a public launch could invite heavy use. Watch memory and CPU after posting.
- **Privacy note:** the site loads fonts from Google Fonts (`fonts.googleapis.com`), so each visit contacts Google. Self-hosting the fonts removes that. This is a small code change, and I have not made it.
- Health check endpoint: `/api/health`.

## 4. Licensing and attribution

### Dependencies (read from the installed packages, 2026-10-22)
- **Frontend runtime:** React, React DOM, React Router, three.js, `@react-three/fiber`, `@react-three/drei`, Radix UI (slider, tabs, toggle group) and Phosphor Icons are all **MIT**.
- **Frontend dev/test tools:** Vite, Vitest, jsdom, oxlint, Testing Library are MIT; TypeScript and Playwright are Apache-2.0.
- **Backend:** FastAPI, SQLModel, pydantic-settings and PyYAML are MIT; httpx, uvicorn and numpy are BSD-3-Clause (numpy's package lists additional bundled-component licences); fastembed is Apache-2.0. onnxruntime (installed with fastembed) was not checked here. **[unverified]**
- **Models:** `BAAI/bge-small-en-v1.5` states **MIT** and says the models "can be used for commercial purposes free of charge" *official*. `Qdrant/bge-small-en-v1.5-onnx-Q` states **MIT** and calls itself a "Quantized ONNX port" of the BAAI model *official*.
- **Fonts:** Instrument Serif, Geist and JetBrains Mono are loaded from Google Fonts. Google Fonts hosts open-source fonts, and I believe all three are SIL Open Font License, but I could not confirm that from the Google page today. **[unverified]**

### Assets and references in the repository
- A scan of `frontend/src` and `frontend/public` found **no third-party images, fonts or media files**; the only asset file is `favicon.svg`. All lesson artwork is drawn in code (three.js and SVG). *measured*
- Lessons quote **short excerpts (at most 30 words each)** from papers and official documentation and always cite the source with a link. The lesson prose and explanations are the project's own. Short, attributed quotation is common practice, but it isn't a licence from those publishers; keep excerpts short as the validator enforces. **[confirm if you want legal review]**
- You mentioned visual references and a "concept image". If any reference image or third-party artwork was *copied* into the app, tell me where so we can record its licence. Taking design inspiration alone doesn't require attribution. **[OWNER]**
- **AI-assisted code:** commits record that Claude Code helped. Your tool's terms govern ownership of its output, and the legal treatment of AI-generated code varies and is still evolving. I did **not** verify Anthropic's current terms here. **[OWNER: read the terms that apply to your plan, and consider a brief legal check before relying on any licence choice]**
- **Name:** I did not check whether "ExplodeAI" conflicts with an existing trademark. **[OWNER]**

### Should the GitHub repo have a licence? Yes, decide one before making it public
There is **no LICENSE file today**. Without one, others have no permission to use or copy the code, even if the repo is public.
- **MIT** or **Apache-2.0** (both permissive, both compatible with the dependencies above). Apache-2.0 adds an explicit patent grant; MIT is shorter and simpler.
- Lesson **content** (text, explanations, source registry) could carry a separate licence (for example CC BY 4.0 so people may share it with credit) or stay all-rights-reserved. This is your choice.
- **Attribution housekeeping I can do on request:** add a `LICENSE` file, and a `THIRD_PARTY_NOTICES.md` listing the dependencies above with their licences. MIT and Apache-2.0 ask that copyright and licence notices travel with redistributed copies, and bundlers often strip those comments from the shipped JavaScript, so a notices file or page is the standard fix.

## 5. Decisions only you can make
1. Which host to try first (and whether you want a custom domain).
2. Whether the repo goes public, and under which licence for code and for content.
3. Whether to make Option A's small code changes, a production Dockerfile, self-hosted fonts, a LICENSE and a notices file. I can do all of these when you say so.

## Sources used for this page
- Render, Deploy for Free: <https://render.com/docs/free>
- Hugging Face, Docker Spaces: <https://huggingface.co/docs/hub/spaces-sdks-docker>
- Hugging Face, Spaces overview (hardware, sleep): <https://huggingface.co/docs/hub/spaces-overview>
- BAAI model card: <https://huggingface.co/BAAI/bge-small-en-v1.5> · Qdrant ONNX card: <https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q>
- Secondary comparisons (verify before relying): <https://flaviocopes.com/hosting-free-tiers/>, <https://getdeploying.com/flyio-vs-koyeb>
