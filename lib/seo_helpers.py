"""SEO helper functions used by build.py and Jinja2 templates.

Pure functions — no I/O, no side effects. Safe to unit test in isolation.
"""
import re


def generate_meta_description(primary, *fallback_sources, max_chars=160, min_chars=70):
    """Return a description string ≤ max_chars, truncated at a sentence
    boundary when one falls in [min_chars, max_chars], otherwise at a word
    boundary.

    `primary` (e.g. an author override) is used as-is when truthy after
    whitespace collapse. Otherwise, the first non-empty `fallback_sources`
    entry is used. Inputs are whitespace-collapsed and lightly
    punctuation-normalised: an internal doubled '.' or '。' that arose from
    naive concatenation collapses to a single terminator; legitimate
    ellipses ('...' / '…') and decimals like '3.14' are preserved.

    `min_chars` bounds sentence-boundary back-off so we never drop below
    validate_seo()'s warning floor; it stays advisory for callers (build.py
    logs a warning at the same threshold).
    """
    candidates = [primary, *fallback_sources]
    for raw in candidates:
        if not raw:
            continue
        cleaned = _normalize_punctuation(_collapse_whitespace(raw))
        # Templates interpolate this into content="..." without autoescape,
        # so a raw double quote would terminate the attribute early.
        cleaned = cleaned.replace('"', "'")
        if not cleaned:
            continue
        return _truncate_at_word_boundary(cleaned, max_chars, min_chars)
    return ""


def _collapse_whitespace(s):
    return re.sub(r"\s+", " ", s).strip()


# Collapse an internal doubled sentence terminator that arose from naive
# concatenation ('University.' + '. Research…' → 'University.. Research…').
# Negative look-arounds preserve legitimate ellipses ('...' has 3 dots —
# left alone) and CJK ellipsis runs.
_DOUBLED_DOT_RE = re.compile(r"(?<!\.)\.{2}(?!\.)")
_DOUBLED_CJK_DOT_RE = re.compile(r"(?<!。)。{2}(?!。)")


def _normalize_punctuation(s):
    if not s:
        return s
    s = _DOUBLED_DOT_RE.sub(".", s)
    s = _DOUBLED_CJK_DOT_RE.sub("。", s)
    return s


_CJK_TERMINATORS = ("。", "！", "？")
_ASCII_TERMINATORS = (".", "!", "?")

# Tokens that commonly precede a '.' inside academic prose; the '.' after
# these is NOT a sentence boundary. Matched case-insensitive against the
# token between the prior whitespace and the '.'.
_ABBREVIATIONS = frozenset({
    "dr", "mr", "mrs", "ms", "st", "jr", "sr",
    "ph.d", "m.d", "b.s", "m.s", "b.a", "m.a",
    "i.e", "e.g", "etc", "vs", "cf", "approx", "ca",
    "no", "vol", "fig", "eq", "pp", "ch", "sec", "p",
    "co", "inc", "ltd", "et", "al",
})


def _is_sentence_boundary(s, i):
    """True iff s[i] terminates a sentence in context.

    CJK terminators ('。', '！', '？') are unambiguous. ASCII terminators
    ('.', '!', '?') are accepted only when followed by whitespace or
    end-of-string AND the token before the '.' is not in _ABBREVIATIONS
    and not a single capital letter (an initial like 'I.', 'J.').
    """
    ch = s[i]
    if ch in _CJK_TERMINATORS:
        return True
    if ch not in _ASCII_TERMINATORS:
        return False
    if i + 1 < len(s) and not s[i + 1].isspace():
        return False
    if ch == ".":
        # Walk back to the prior whitespace; token = chars between space and '.'.
        j = i - 1
        while j >= 0 and not s[j].isspace():
            j -= 1
        token = s[j + 1:i].lower()
        if token in _ABBREVIATIONS:
            return False
        # Single capital letter before '.' = initial (I., J., A.).
        if len(token) == 1 and s[i - 1].isupper():
            return False
    return True


def _truncate_at_word_boundary(s, max_chars, min_chars=0):
    if len(s) <= max_chars:
        return s
    cut = s[:max_chars]
    # 1) Prefer the latest sentence boundary in [min_chars, max_chars] so the
    #    snippet reads as a finished thought; the terminator is retained.
    floor = max(min_chars - 1, 0)
    for i in range(len(cut) - 1, floor, -1):
        if _is_sentence_boundary(cut, i):
            return cut[: i + 1].rstrip(" ,;:")
    # 2) Fall back to the prior word-boundary behaviour: last ASCII space.
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
