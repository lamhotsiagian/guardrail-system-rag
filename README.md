# Guardrail System RAG — Production Recommendation Systems & RAG Course Stack

An interactive, chat-driven learning system and production reference architecture for recommendation-system engineering with layered LLM guardrails, built with FastAPI, LangGraph, Ollama, and pgvector, fronted by a modern Next.js / React 19 App Router lab UI. Every recommender concept — explicit/implicit feedback, collaborative and content-based filtering, hybrids, cold-start, evaluation, sequential and neural models, ANN candidate generation, matrix factorization, and production serving/MLOps — is implemented as a real, multi-tenant backend module you can trigger live from the chat interface via **/**-prefixed slash commands.

Every chat turn flows through a guarded LangGraph pipeline (L1 input guard → L3 intent/topic routing → L4 topic boundary & dedup → L5 tool-argument gate with human-in-the-loop confirmation → L6 indirect-injection neutralisation → L9 audit trail), so the same stack doubles as a working reference for LLM guardrail engineering.

---

## Features

- Agentic RAG & Slash Command Interceptor: LangGraph routes **/**-prefixed commands to a local math executor (CF, SVD, TF-IDF, ANN) and free-text messages through the guarded LLM RAG theory pipeline.
- Layered Guardrails (**backend/app/guardrails/**): deterministic input validators (normalization, PII redaction, injection heuristics), LLM classifier tier (**llama3.2:1b**), semantic topic/intent centroids, tool-argument gating with HITL interrupts for destructive commands, poisoned-document neutralisation, rate limiting, token caps, circuit breaker, and a full **guard_audit** verdict trail in Postgres.
- Interactive Curriculum (10 chapters): **/classify-feedback**, **/tenant-similar-users**, **/memory-user-profile**, **/hybrid-mix-full**, **/warm-start-sim**, **/tenant-evaluate**, **/memory-sequence-train**, **/tenant-scoped-ann**, **/capstone-train** + **/capstone-recommend**, **/progress**, **/memory-report**.
- Data Lifecycle & Reversibility: predefined seeds, non-deterministic scale generation with reproducible **seed** inputs, and reversible resets that wipe only generated rows via a **source** tracking tag — organic user activity is never touched.
- Modern Lab Dashboard: slash-command autocomplete, interactive table renderer, 1-click **needs_seed** suggestion chips, sidebar progress tracker, and a Data Lab page for seeding/generating/resetting without the chat.
- Reproducible benchmarks (**benchmarks/**): standalone scripts measuring HNSW vs brute-force retrieval, MF RMSE / HR@10 / NDCG@10, a two-tower with in-batch negatives, MMR re-ranking, a cold-start bandit, and guard latency.

## Tech Stack

- Backend / API: Python 3.12, FastAPI, Uvicorn, Pydantic v2 + pydantic-settings.
- Agent / RAG orchestration: LangGraph (+ Postgres checkpointer), LangChain (**langchain-ollama**, **langchain-postgres**, **langchain-community**).
- LLM & embeddings: Ollama running **llama3.1** (chat/judge), **llama3.2:1b** (guard classifier), and **nomic-embed-text** (768-dim embeddings).
- Data layer: PostgreSQL 16 + pgvector (**Vector(768)**, HNSW/IVFFlat), SQLAlchemy 2 (async), **asyncpg** / **psycopg 3**.
- Auth & security: JWT (PyJWT), bcrypt/passlib hashing, multi-tenant **tenant_id** isolation on every query.
- Frontend: Next.js (App Router) + React 19, TypeScript 5, Tailwind CSS 4, streaming (NDJSON) chat.
- Testing: pytest (unit + adversarial corpus), headless graph smoke test, Playwright end-to-end UI suite with per-test screenshots.

Read the details:# guardrail-system-rag
# guardrail-system-rag
