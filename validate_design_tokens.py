"""Design-token invariants for the E3 Center site.

Mirrors validate_member.py: run standalone, exit non-zero on failure.
Three invariants, each mapping to a rule in DESIGN_RULES/:

  1. Every --cat-*-text colour clears WCAG AA (4.5:1) both on its own tinted
     badge background and on the page background (the phone bare-label case).
  2. No deprecated --fs-* alias is referenced anywhere.
  3. No component rule consumes a raw primitive (--r-*, --*-light, --house-*)
     directly; primitives are reachable only through a semantic alias or the
     illustration utility layer.
"""
import re
import sys
from pathlib import Path

CSS_DIR = Path("static/css")
GENERAL = CSS_DIR / "general.css"
PAGE_BG = "#f7fafb"
AA = 4.5

# Deprecated aliases retired by the v3 token ladder.
DEPRECATED_ALIASES = [
    "fs-display-xl", "fs-display-l", "fs-display-m", "fs-display-s",
    "fs-heading-l", "fs-heading-m", "fs-heading-s",
    "fs-body-xl", "fs-body-l", "fs-body-s",
    "fs-caption", "fs-caption-s", "fs-prose-lede", "lh-prose",
]

# Primitives: raw hues that only the illustration layer may consume directly.
PRIMITIVE_RE = re.compile(r"var\(--(r-[a-z]+|main-light|main-3-light|secondary-light|house-dark|house-light)\)")
# Selectors that ARE the illustration layer. Matched against the enclosing
# selector, never the declaration line — `.fill-r-green { fill: var(--r-green) }`
# puts the selector and the declaration on different lines.
ILLUSTRATION_SELECTOR_RE = re.compile(r"^\.(fill|stroke)-")


def _srgb(hex_colour):
    h = hex_colour.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def _luminance(hex_colour):
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
         for x in _srgb(hex_colour)]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _mix(a, b, pct_a):
    ca, cb = _srgb(a), _srgb(b)
    return "#%02x%02x%02x" % tuple(
        round(255 * (ca[i] * pct_a + cb[i] * (1 - pct_a))) for i in range(3))


def _read_root_tokens(css):
    """Map token name -> raw value string, from every :root-level declaration."""
    tokens = {}
    for name, value in re.findall(r"^\s+--([a-z0-9-]+):\s*([^;]+);", css, re.M):
        tokens.setdefault(name, value.strip())
    return tokens


def resolve(value, tokens, depth=0):
    """Resolve a token value to a #rrggbb hex string.

    Handles the three forms the stylesheet actually uses: a literal hex, a
    var() reference, and color-mix(in srgb, <colour> N%, <colour>).
    Returns None for anything else (e.g. keywords like `transparent`).
    """
    if depth > 8:
        return None
    value = value.strip()

    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return value.lower()

    var_match = re.fullmatch(r"var\(--([a-z0-9-]+)\)", value)
    if var_match:
        inner = tokens.get(var_match.group(1))
        return resolve(inner, tokens, depth + 1) if inner else None

    if value.startswith("color-mix("):
        inner = value[len("color-mix("):]
        if inner.endswith(")"):
            inner = inner[:-1]
        parts = [p.strip() for p in _split_top_level(inner)]
        if len(parts) == 3 and parts[0] == "in srgb":
            first, second = parts[1], parts[2]
            pct_match = re.search(r"(\d+(?:\.\d+)?)%", first)
            if not pct_match:
                return None
            pct = float(pct_match.group(1)) / 100
            c1 = resolve(first[:pct_match.start()].strip(), tokens, depth + 1)
            c2 = resolve(re.sub(r"\s*\d+(?:\.\d+)?%", "", second).strip(), tokens, depth + 1)
            if c1 and c2:
                return _mix(c1, c2, pct)
    return None


def _split_top_level(text):
    """Split on commas that are not inside parentheses."""
    parts, depth, current = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    parts.append(current)
    return parts


def check_category_contrast():
    css = GENERAL.read_text(encoding="utf-8")
    tokens = _read_root_tokens(css)
    failures = []
    for name in sorted(t for t in tokens if t.startswith("cat-") and t.endswith("-text")):
        base = name[:-len("-text")]
        text_hex = resolve(tokens[name], tokens)
        base_hex = resolve(tokens.get(base, ""), tokens)
        if not text_hex or not base_hex:
            failures.append(f"--{name}: could not resolve to a hex colour")
            continue
        # Badge tint: the base hue mixed over white. 13% is the listing default;
        # faculty uses 22% and outreach 14%. Test the lightest (weakest) case.
        tint = _mix(base_hex, "#ffffff", 0.13)
        on_tint = contrast(text_hex, tint)
        on_page = contrast(text_hex, PAGE_BG)
        if min(on_tint, on_page) < AA:
            failures.append(
                f"--{name} ({text_hex}): {on_tint:.2f}:1 on tint, "
                f"{on_page:.2f}:1 on page bg — below AA {AA}:1")
    return failures


def check_deprecated_aliases():
    failures = []
    for css_file in sorted(CSS_DIR.glob("*.css")):
        for lineno, line in enumerate(css_file.read_text(encoding="utf-8").splitlines(), 1):
            for alias in DEPRECATED_ALIASES:
                if f"var(--{alias})" in line:
                    failures.append(f"{css_file}:{lineno}: deprecated var(--{alias})")
    return failures


def check_primitive_leakage():
    """Flag primitives used outside :root and outside the illustration layer.

    Tracks the enclosing selector stack rather than testing the declaration
    line, because a rule's selector and its declarations are on different
    lines — `.fill-r-green { fill: var(--r-green); }` is legitimate and must
    not be reported.
    """
    failures = []
    for css_file in sorted(CSS_DIR.glob("*.css")):
        depth = 0
        stack = []  # list of (depth_at_open, selector_text)
        for lineno, line in enumerate(css_file.read_text(encoding="utf-8").splitlines(), 1):
            opens, closes = line.count("{"), line.count("}")
            if opens:
                stack.append((depth, line.split("{")[0].strip()))
            exempt = any(
                sel == ":root" or ILLUSTRATION_SELECTOR_RE.match(sel)
                for _, sel in stack)
            if not exempt and PRIMITIVE_RE.search(line):
                failures.append(
                    f"{css_file}:{lineno}: component rule consumes a primitive directly "
                    f"— add a semantic alias in :root first")
            depth += opens - closes
            while stack and stack[-1][0] >= depth:
                stack.pop()
    return failures


def main():
    all_failures = []
    for label, check in (
        ("category contrast", check_category_contrast),
        ("deprecated aliases", check_deprecated_aliases),
        ("primitive leakage", check_primitive_leakage),
    ):
        failures = check()
        status = "OK" if not failures else f"{len(failures)} failure(s)"
        print(f"{label:<22} {status}")
        for failure in failures:
            print(f"    {failure}")
        all_failures.extend(failures)
    print()
    if all_failures:
        print(f"Design token check: {len(all_failures)} failure(s).")
        return 1
    print("Design token check: 0 failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
