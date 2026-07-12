# Guardrails package (ten-layer stack)

Companion code for the ebook *Guardrails Engineering for RAG Systems* (`../../../ebook/`).
One module per layer; `graph.py` wires them around the existing slash/RAG pipeline.

## Setup

```bash
ollama pull llama3.2:1b                                  # guard classifier
psql $DATABASE_URL -f backend/scripts/migrations/002_guardrails.sql
python -m scripts.seed_centroids                         # chapter centroids (L3/L4)
```

Register the rate-limit middleware in `app/middleware.py`:

```python
from app.guardrails import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)
```

Build the guarded graph in place of `build_retrival_graph` (see `graph.py`
docstring for the injected pipeline nodes).

## Tests & benchmarks

```bash
pytest tests/guardrails -m "not integration"     # unit tier, no services
pytest tests/guardrails -m integration           # needs Ollama + Postgres
python benchmarks/guard_latency.py --iters 50    # p50/p95 per layer
```

| Module | Layer | Book chapter |
|---|---|---|
| validators.py, input_guard.py | L1 | 3 |
| intent_guard.py | L3 | 4 |
| doc_screen.py | L6 | 5 |
| tool_gate.py | L5 | 6 |
| semantic_guard.py | L4 | 7 |
| output_guard.py | L2 | 8 |
| budget.py | L7 | 9 |
| audit.py, graph.py | L9/L10 | 10 |
