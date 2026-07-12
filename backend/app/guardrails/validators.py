"""Shared deterministic validators: normalization, PII, injection heuristics.

Tier-0 guards. Everything in this module is pure code — no model calls, no
database — so it runs in microseconds and is trivially unit-testable
(``tests/guardrails/test_input_guard.py``).
"""

import re
import unicodedata

from .config import guard_settings

# --- Slash-command shape (mirrors app.course.routes.parse_slash_command) ----
SLASH_RE = re.compile(r"^/[a-z][a-z0-9-]*")

# --- PII patterns ------------------------------------------------------------
# Deterministic redaction before any text reaches the LLM, the embedder, or a
# memory record. Swap in Microsoft Presidio for entity-level NER if the
# deployment's privacy bar requires it; keep these regexes as the fast path.
PII_PATTERNS: dict[str, re.Pattern] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)[\s.-]?)?\d{3,4}[\s.-]?\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}

# --- Indirect-injection heuristics for retrieved chunks (L6) ------------------
# Instruction-shaped text inside reference documents is the signature of
# indirect prompt injection (Greshake et al., 2023).
INSTRUCTION_PATTERN = re.compile(
    r"(?i)\b(ignore (all|previous|above)|disregard (the|all|previous)"
    r"|you are now|new instructions?:|system prompt|do not follow"
    r"|instead,? (do|say|run|execute)|run the command|type /)",
)

# --- Suspicious argument content for slash commands (L5) ---------------------
SQL_FRAGMENT_RE = re.compile(
    r"(?i)(;|--|\b(drop|delete|truncate|update|insert|alter|grant)\b)"
)


def normalize_input(raw: str, max_chars: int | None = None) -> str:
    """NFKC-normalize, strip control chars, and cap length.

    NFKC folds homoglyph tricks (full-width chars, ligatures) that attackers
    use to slip past keyword filters; the cap bounds classifier and embedding
    cost before anything downstream runs.
    """
    cap = max_chars or guard_settings.max_input_chars
    text = unicodedata.normalize("NFKC", raw)
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in "\n\t")
    return text[:cap]


def redact_pii(text: str) -> tuple[str, dict[str, int]]:
    """Replace PII spans with typed placeholders; report counts per type.

    Returns the redacted text and a ``{pii_type: count}`` map so the caller
    can log *that* redaction happened without logging *what* was redacted.
    """
    counts: dict[str, int] = {}
    for pii_type, pattern in PII_PATTERNS.items():
        text, n = pattern.subn(f"[{pii_type.upper()}_REDACTED]", text)
        if n:
            counts[pii_type] = n
    return text, counts


def neutralize(chunk_text: str) -> str:
    """Defang instruction-shaped lines inside a retrieved document chunk.

    We keep the chunk (it may still carry useful content) but wrap the
    offending lines so the generator sees them as quoted data, not directives.
    """
    lines = []
    for line in chunk_text.splitlines():
        if INSTRUCTION_PATTERN.search(line):
            lines.append(f"[quoted, non-instructional text] {line}")
        else:
            lines.append(line)
    return "\n".join(lines)


def looks_like_slash(text: str) -> bool:
    """True when the message should route to the deterministic command path."""
    return bool(SLASH_RE.match(text.strip()))
