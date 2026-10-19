# Scaling notes (and why there is no Kubernetes yet)

Today ExplodeAI is two processes (FastAPI + a static/Vite frontend) and one
SQLite file. Experiments run on tiny corpora in milliseconds (see the timing
strip). That is the right shape for local development and a small public
deployment: one container host, or the API on a PaaS with the frontend on a CDN.

What would change, and when:

| Trigger | Change |
|---|---|
| Concurrent writers or more than one API replica | Move SQLite → Postgres (SQLModel makes this a `DATABASE_URL` change plus migrations, e.g. Alembic). |
| Learners upload their own corpora, or neural embedding at scale | Queue embedding jobs (a worker + Redis/SQS), cache embeddings by content hash, store vectors in pgvector or FAISS. |
| Paid AI enabled for the public | Move the budget/rate ledger to Postgres or Redis so limits hold across replicas; add per-user auth before any paid feature. |
| Several API replicas with autoscaling, rolling deploys, and separate worker pools | This is where Kubernetes (or a managed container service) starts to pay for itself. Until then it adds operational cost without benefit. |

The frontend is static after `npm run build` and can be served from any CDN.
three.js is already split into a lazy chunk.
