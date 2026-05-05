"""SEO helper functions used by build.py and Jinja2 templates.

Pure functions — no I/O, no side effects. Safe to unit test in isolation.
"""
import re


def generate_meta_description(primary, *fallback_sources, max_chars=160, min_chars=70):
    """Return a description string ≤ max_chars, truncated at word boundary.

    `primary` (e.g. an author override) is used as-is when truthy after
    whitespace collapse. Otherwise, the first non-empty `fallback_sources`
    entry is used. All inputs are whitespace-collapsed.

    The min_chars argument is informational only — used by validate_seo()
    to flag too-short descriptions, not enforced here.
    """
    candidates = [primary, *fallback_sources]
    for raw in candidates:
        if not raw:
            continue
        cleaned = _collapse_whitespace(raw)
        if not cleaned:
            continue
        return _truncate_at_word_boundary(cleaned, max_chars)
    return ""


def _collapse_whitespace(s):
    return re.sub(r"\s+", " ", s).strip()


def _truncate_at_word_boundary(s, max_chars):
    if len(s) <= max_chars:
        return s
    cut = s[:max_chars]
    # Walk back to last whitespace so we don't cut mid-word
    last_space = cut.rfind(" ")
    if last_space > 0:
        return cut[:last_space].rstrip(" ,;:.")
    return cut.rstrip(" ,;:.")
