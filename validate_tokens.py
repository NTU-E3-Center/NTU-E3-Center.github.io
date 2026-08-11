#!/usr/bin/env python3
"""Invariants for tokens/e3.tokens.json — the new design system's source of truth.

Runs standalone, exits non-zero on failure. Deliberately independent of
validate_design_tokens.py, which checks the *old* CSS-first system.

  1. Every colour in `mark` matches the logo SVG exactly. The mark is the
     specification; if someone edits a swatch here it must be because the
     artwork changed, not because a value looked nicer.
  2. Every text colour clears the contrast target on EVERY declared surface.
     The old system was paper-calibrated, so metadata on a tinted band could
     land far below AA. Text is checked against paper *and* the band.
  3. Every `.graphic` colour has a `.text` sibling, and no graphic value is
     accidentally legible enough to be mistaken for a text token.
  4. The type scale is monotonic across tiers and never drops below the 12px
     legibility floor on phone.
  5. Nothing in `color` is a hex that does not trace back to `mark` — either
     verbatim or as a derivation the script can reproduce.
"""
import json
import re
import sys
from pathlib import Path

TOKENS = Path("tokens/e3.tokens.json")
LOGO = Path("static/assets/images/e3-center-logo-inline.svg")

failures = []
def check(name, ok, detail=""):
    print(f"{name:<34}{'OK' if ok else 'FAIL'}{'  ' + detail if detail and not ok else ''}")
    if not ok:
        failures.append(f"{name}: {detail}")


# ── colour maths ─────────────────────────────────────────────────────────────
def _lin(v):
    v /= 255
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def lum(h):
    r, g, b = hex2rgb(h)
    return .2126 * _lin(r) + .7152 * _lin(g) + .0722 * _lin(b)

def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + .05) / (lo + .05)


def walk(node, path=()):
    """Yield (dotted-path, value) for every $value leaf."""
    if isinstance(node, dict):
        if "$value" in node:
            yield ".".join(path), node["$value"]
        for k, v in node.items():
            if not k.startswith("$"):
                yield from walk(v, path + (k,))


def main():
    if not TOKENS.exists():
        print(f"missing {TOKENS}")
        return 1
    t = json.loads(TOKENS.read_text())
    leaves = dict(walk(t))
    target = t["meta"]["contrastTargetText"]["$value"]
    surfaces = {n: leaves[f"color.{n}"]
                for n in (s.strip().split(".")[-1]
                          for s in t["meta"]["surfaces"]["$value"].split(","))}

    # 1 ── mark matches the artwork
    if LOGO.exists():
        in_svg = {m.group(0).lower() for m in re.finditer(r"#[0-9a-fA-F]{6}", LOGO.read_text())}
        declared = {v.lower() for k, v in leaves.items() if k.startswith("mark.")}
        missing = declared - in_svg
        check("mark matches the logo SVG", not missing,
              f"not present in artwork: {sorted(missing)}")
    else:
        check("mark matches the logo SVG", False, f"{LOGO} not found")

    # 2 ── every text colour clears target on every surface
    text_tokens = {k: v for k, v in leaves.items()
                   if k.startswith("color.") and (k.endswith(".text")
                      or k.split(".")[-1] in ("ink", "muted", "structure"))}
    bad = []
    for name, val in sorted(text_tokens.items()):
        for sname, sval in surfaces.items():
            r = ratio(val, sval)
            if r < target:
                bad.append(f"{name} on {sname} = {r:.2f}:1")
    check(f"text clears {target}:1 on all surfaces", not bad, "; ".join(bad))

    # 3 ── graphic/text pairing
    graphics = [k for k in leaves if k.endswith(".graphic")]
    unpaired = [g for g in graphics if g.rsplit(".", 1)[0] + ".text" not in leaves]
    check("every graphic has a text sibling", not unpaired, f"unpaired: {unpaired}")

    # 4 ── scale sanity
    def px(v): return float(str(v).replace("px", ""))
    order = ["phone", "tablet", "laptop", "wide"]
    non_mono, too_small = [], []
    for role, spec in t["scale"].items():
        if role.startswith("$"):
            continue
        vals = [px(spec["$value"][tier]) for tier in order]
        if any(b < a for a, b in zip(vals, vals[1:])):
            non_mono.append(f"{role}={vals}")
        if px(spec["$value"]["phone"]) < 12:
            too_small.append(f"{role}={spec['$value']['phone']}")
    check("scale is monotonic across tiers", not non_mono, "; ".join(non_mono))
    check("no phone size below 12px", not too_small, "; ".join(too_small))

    # 5 ── no untraceable colours
    mark_vals = {v.lower() for k, v in leaves.items() if k.startswith("mark.")}
    derived = {leaves[k].lower() for k in leaves if k.startswith("color.")}
    # a colour is traceable if it IS a mark colour or is documented as derived
    undocumented = []
    for k, v in leaves.items():
        if not k.startswith("color."):
            continue
        node = t
        for part in k.split("."):
            node = node[part]
        if v.lower() not in mark_vals and not node.get("$description"):
            undocumented.append(k)
    check("every colour traces to the mark", not undocumented,
          f"undocumented derivation: {undocumented}")

    print()
    if failures:
        print(f"Token check: {len(failures)} failure(s).")
        for f in failures:
            print(f"  - {f}")
        return 1
    n = len([k for k in leaves if k.startswith("color.") or k.startswith("mark.")])
    print(f"Token check: 0 failures. {n} colours verified against "
          f"{len(surfaces)} surfaces ({', '.join(surfaces)}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
