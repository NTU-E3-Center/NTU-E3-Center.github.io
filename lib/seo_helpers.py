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


_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^\)]*\)")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^\)]*\)")
_MD_CODE_RE = re.compile(r"`([^`]+)`")
_MD_BOLD_ITALIC_RE = re.compile(r"(\*{1,3}|_{1,3})(.+?)\1")
_MD_HEADING_RE = re.compile(r"^#{1,6}\s+", flags=re.MULTILINE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_CJK_RE = re.compile(r"[一-鿿㐀-䶿]")


def strip_markdown(text):
    """Remove markdown syntax for use in plain-text contexts (meta descriptions).

    Drops images entirely. Keeps link/bold/italic/code text, drops their syntax.
    Strips HTML tags. Collapses whitespace.
    """
    if not text:
        return ""
    text = _MD_IMAGE_RE.sub("", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _MD_CODE_RE.sub(r"\1", text)
    text = _MD_BOLD_ITALIC_RE.sub(r"\2", text)
    text = _MD_HEADING_RE.sub("", text)
    text = _HTML_TAG_RE.sub("", text)
    return _collapse_whitespace(text)


def detect_language(text, threshold=0.3):
    """Return 'zh-TW' if CJK character ratio >= threshold, else 'en'."""
    if not text:
        return "en"
    total = len(text)
    cjk = len(_CJK_RE.findall(text))
    return "zh-TW" if (cjk / total) >= threshold else "en"
