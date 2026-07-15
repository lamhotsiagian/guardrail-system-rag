"""Ten-layer guardrail stack for the recommendation-system-rag app.

Each module is one layer from the book "Guardrails Engineering for RAG
Systems"; the final wiring lives in ``graph.py`` / ``integration.py``.

Import policy: the lightweight, dependency-free names (config, state,
validators) are imported eagerly. Everything that pulls heavy deps
(sqlalchemy, langchain, langgraph-postgres) is loaded lazily via PEP 562
``__getattr__`` so that ``from app.guardrails import guard_settings`` -- or a
unit test importing only the deterministic validators -- does not drag in the
whole runtime stack. Public import surface is unchanged.
"""

import importlib
from typing import TYPE_CHECKING

# --- Eager, lightweight ------------------------------------------------------
from .config import guard_settings
from .policy import policy_registry
from .state import GuardedState, GuardVerdict
from .validators import (looks_like_slash, neutralize, normalize_input,
                         redact_pii)

# --- Lazy map: public name -> submodule that defines it ----------------------
# The legacy pattern constants route through here on purpose: each access
# resolves against the live policy pack (hot-reload aware) instead of a
# snapshot taken at import time.
_LAZY: dict[str, str] = {
    "PII_PATTERNS": "validators", "INSTRUCTION_PATTERN": "validators",
    "SQL_FRAGMENT_RE": "validators",
    "input_guard": "input_guard", "InputVerdict": "input_guard",
    "intent_router": "intent_guard", "route_by_intent": "intent_guard",
    "Intent": "intent_guard",
    "doc_screen": "doc_screen", "CONTEXT_CONTRACT": "doc_screen",
    "tool_gate": "tool_gate", "validate_args": "tool_gate",
    "DESTRUCTIVE": "tool_gate", "EXPENSIVE": "tool_gate",
    "semantic_guard": "semantic_guard", "NLIVerdict": "semantic_guard",
    "output_guard": "output_guard", "StreamGuard": "output_guard",
    "Grounding": "output_guard",
    "budget_guard": "budget", "rate_limit_middleware": "budget",
    "OllamaCircuitBreaker": "budget", "ollama_breaker": "budget",
    "audit_write": "audit", "flush_verdicts": "audit",
    "get_guarded_graph": "integration", "run_guarded_stream": "integration",
    "resume_guarded_stream": "integration", "resolve_tenant_id": "integration",
    "retriever_node": "nodes", "generate_node": "nodes",
    "json_complete": "llm_json", "make_json_model": "llm_json",
    "nav_helper_node": "nodes",
}


def __getattr__(name: str):  # PEP 562: import heavy submodules on first use
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module 'app.guardrails' has no attribute '{name}'")
    mod = importlib.import_module(f".{module}", __name__)
    return getattr(mod, name)


if TYPE_CHECKING:  # help static analysers / IDEs see the lazy names
    from .audit import audit_write, flush_verdicts
    from .budget import (OllamaCircuitBreaker, budget_guard, ollama_breaker,
                         rate_limit_middleware)
    from .doc_screen import CONTEXT_CONTRACT, doc_screen
    from .input_guard import InputVerdict, input_guard
    from .integration import (get_guarded_graph, resolve_tenant_id,
                              resume_guarded_stream, run_guarded_stream)
    from .intent_guard import Intent, intent_router, route_by_intent
    from .nodes import generate_node, nav_helper_node, retriever_node
    from .output_guard import Grounding, StreamGuard, output_guard
    from .semantic_guard import NLIVerdict, semantic_guard
    from .tool_gate import DESTRUCTIVE, EXPENSIVE, tool_gate, validate_args

__all__ = [
    "guard_settings", "policy_registry", "GuardedState", "GuardVerdict",
    "normalize_input", "redact_pii", "looks_like_slash", "neutralize",
    "PII_PATTERNS", "SQL_FRAGMENT_RE", "INSTRUCTION_PATTERN",
    "input_guard", "InputVerdict",
    "intent_router", "route_by_intent", "Intent",
    "doc_screen", "CONTEXT_CONTRACT",
    "tool_gate", "validate_args", "DESTRUCTIVE", "EXPENSIVE",
    "semantic_guard", "NLIVerdict",
    "output_guard", "StreamGuard", "Grounding",
    "budget_guard", "rate_limit_middleware",
    "OllamaCircuitBreaker", "ollama_breaker",
    "audit_write", "flush_verdicts",
    "get_guarded_graph", "run_guarded_stream", "resume_guarded_stream",
    "resolve_tenant_id", "retriever_node", "generate_node", "nav_helper_node",
]
