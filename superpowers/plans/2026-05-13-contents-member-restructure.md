# Per-Member Content Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `contents/` into per-member folders so each member's data (position, emails, interests, links, bio) lives in `contents/members/{webId}/{member.json, about.md, photo.{ext}}`. Excel keeps the 11 admin columns and acts as a roster.

**Architecture:** Two-source merge at build time. `lib/excel_to_content.py` reads admin fields from Excel + content fields from the per-member folder, validates the JSON against a schema (build fails on errors, warns on missing optional files), and merges into the per-member dict templates already consume — so templates are untouched. A one-time, committed migration script bootstraps the new structure from the existing 22-column Excel + the old per-member markdown files.

**Tech Stack:** Python 3.9, openpyxl, json (stdlib), pathlib (stdlib), unittest (stdlib). No new runtime deps.

**Spec:** `superpowers/specs/2026-05-13-contents-member-restructure-design.md`
**Branch:** `feat/member-content-restructure` (already created from `source`, spec committed at `66ddbac`)

---

## Path convention note (read before Task 0)

The spec assumes a `lib/` package exists (PR #12 `chore/lib-folder-and-deps-cleanup`). At plan-execution time `lib/` may or may not exist depending on whether #12 merged into `source` first.

**Task 0 resolves this.** Every later task references `<LIB>` as a placeholder. After Task 0, perform a global mental substitution:

| Context | POST_CHORE (lib/ exists) | PRE_CHORE (no lib/) |
|---|---|---|
| Path string (e.g. `<LIB>validate_member.py`) | `lib/validate_member.py` | `validate_member.py` |
| Python import (e.g. `from <LIB>validate_member`) | `from lib.validate_member` | `from validate_member` |
| Test imports in `tests/test_*.py` written below as `from lib.X` | unchanged: `from lib.X` | substitute: `from X` |

The plan body is written assuming POST_CHORE for readability. If Task 0 detects PRE_CHORE, strip the `lib/` prefix from paths and the `lib.` prefix from imports as you execute each task.

---

## Phase 0 — Branch sync & path decision

### Task 0: Verify branch + decide module location

**Files:**
- Read: `lib/__init__.py` (if it exists)
- Read: `lib/excel_to_content.py` (if it exists) OR `excel_to_content.py` (otherwise)

- [ ] **Step 1: Confirm working tree state**

Run:
```bash
git branch --show-current
git status -s
git log -1 --oneline
```

Expected:
```
feat/member-content-restructure
(empty or only the SEO untracked dirs)
66ddbac docs(spec): design for per-member content restructure
```

If the branch isn't `feat/member-content-restructure`, abort and resync: `git checkout feat/member-content-restructure`.

- [ ] **Step 2: Detect module root**

Run:
```bash
if [ -f lib/__init__.py ]; then echo "POST_CHORE"; else echo "PRE_CHORE"; fi
```

Record the result. **For the remainder of the plan, replace `<LIB>` with:**
- POST_CHORE → `lib/` (e.g. `lib/validate_member.py`, `from lib.validate_member import ...`)
- PRE_CHORE → `` (e.g. `validate_member.py`, `from validate_member import ...`)

- [ ] **Step 3: If PRE_CHORE, consider rebasing onto the chore branch**

Decision tree:
- **If chore PR #12 is unmerged but close to merging:** wait, let it merge, then `git fetch && git rebase origin/source` here.
- **If chore PR #12 is blocked or far from merging:** continue in PRE_CHORE mode. The new modules will live at repo root; when #12 eventually merges they'll get moved into `lib/` as part of that merge.
- **If chore PR #12 has merged:** confirm `source` is updated, then `git rebase origin/source`.

This is a decision step — no commands required, just judgment. Document the choice in a one-line commit message later (`feat: choose <LIB> = lib/ (post #12 merge)` or similar).

- [ ] **Step 4: Confirm baseline build still works**

Run:
```bash
conda run -n E3website python build.py 2>&1 | tail -3
```

Expected: `Build complete!`

If the build fails, stop and investigate before touching anything else.

- [ ] **Step 5: Capture a pre-change snapshot of `docs/`**

Run:
```bash
rm -rf /tmp/docs.before
cp -r docs /tmp/docs.before
```

This snapshot is the golden file we'll diff against after each refactor step to confirm zero rendering regressions.

- [ ] **Step 6: Commit nothing — Task 0 is observational**

No commit yet. Proceed to Phase 1.

---

## Phase 1 — Validation module (TDD)

### Task 1: Scaffold `validate_member.py` + dataclass

**Files:**
- Create: `<LIB>validate_member.py`
- Create: `tests/test_validate_member.py`

- [ ] **Step 1: Write the failing test for the public signature**

Create `tests/test_validate_member.py`:
```python
import unittest
from pathlib import Path
import tempfile
import os

# Import path depends on <LIB>; replace `lib.validate_member` with
# `validate_member` if PRE_CHORE.
from lib.validate_member import validate_member_folder, ValidationIssue


class TestValidateMemberFolder(unittest.TestCase):
    def test_returns_list_of_validation_issues(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "missing"
            issues = validate_member_folder("nobody", folder)
            self.assertIsInstance(issues, list)
            self.assertTrue(all(isinstance(i, ValidationIssue) for i in issues))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test, confirm it fails**

Run:
```bash
conda run -n E3website python -m unittest tests.test_validate_member -v
```

Expected: `ModuleNotFoundError: No module named 'lib.validate_member'`

- [ ] **Step 3: Create the module with the dataclass and a stub function**

Create `<LIB>validate_member.py`:
```python
"""Per-member folder validation for the build pipeline.

Used by lib/excel_to_content.py to verify contents/members/{webId}/
folders before the build proceeds. Errors fail the build; warnings
log but allow the build to continue (so a half-onboarded new member
does not block deploys)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ValidationIssue:
    severity: str   # "error" | "warn"
    message: str

    def __post_init__(self) -> None:
        if self.severity not in ("error", "warn"):
            raise ValueError(f"severity must be 'error' or 'warn', got {self.severity!r}")


def validate_member_folder(web_id: str, folder: Path) -> list[ValidationIssue]:
    """Inspect a per-member content folder and return any issues found.

    Empty list = OK. See severities in the dataclass docstring above."""
    return []
```

- [ ] **Step 4: Run the test, confirm it passes**

Run:
```bash
conda run -n E3website python -m unittest tests.test_validate_member -v
```

Expected:
```
test_returns_list_of_validation_issues (...) ... ok
Ran 1 test in 0.00...s
OK
```

- [ ] **Step 5: Commit**

```bash
git add <LIB>validate_member.py tests/test_validate_member.py
git commit -m "feat(validate_member): scaffold module + dataclass

ValidationIssue carries severity ('error' | 'warn') + message.
validate_member_folder is a stub returning []; will be filled in
case-by-case via TDD in subsequent tasks."
```

---

### Task 2: Folder-missing warning

**Files:**
- Modify: `tests/test_validate_member.py`
- Modify: `<LIB>validate_member.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_validate_member.py` (inside `TestValidateMemberFolder`):
```python
    def test_folder_missing_yields_one_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "nonexistent"
            issues = validate_member_folder("nobody", folder)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0].severity, "warn")
            self.assertIn("folder missing", issues[0].message)
```

- [ ] **Step 2: Run, confirm fail**

Run: `conda run -n E3website python -m unittest tests.test_validate_member -v`
Expected: `FAIL: test_folder_missing_yields_one_warning` (issues is `[]`)

- [ ] **Step 3: Implement the check**

In `<LIB>validate_member.py`, replace `validate_member_folder`:
```python
def validate_member_folder(web_id: str, folder: Path) -> list[ValidationIssue]:
    """Inspect a per-member content folder and return any issues found."""
    issues: list[ValidationIssue] = []

    if not folder.is_dir():
        issues.append(ValidationIssue(
            "warn",
            f"{folder}: folder missing — build will render a placeholder profile.",
        ))
        return issues

    return issues
```

- [ ] **Step 4: Run, confirm pass**

Run: `conda run -n E3website python -m unittest tests.test_validate_member -v`
Expected: 2 tests OK.

- [ ] **Step 5: Commit**

```bash
git add <LIB>validate_member.py tests/test_validate_member.py
git commit -m "feat(validate_member): warn when member folder is missing"
```

---

### Task 3: member.json missing

**Files:**
- Modify: `tests/test_validate_member.py`
- Modify: `<LIB>validate_member.py`

- [ ] **Step 1: Failing test**

Append:
```python
    def test_member_json_missing_yields_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "empty"
            folder.mkdir()
            issues = validate_member_folder("empty", folder)
            severities = [(i.severity, "member.json" in i.message) for i in issues]
            self.assertIn(("warn", True), severities)
```

- [ ] **Step 2: Run, confirm fail**

Expected: AssertionError (no member.json-related issue yet).

- [ ] **Step 3: Implement**

Append inside `validate_member_folder` (before the final `return issues`):
```python
    member_json = folder / "member.json"
    if not member_json.exists():
        issues.append(ValidationIssue(
            "warn",
            f"{member_json}: member.json missing — profile will render with defaults.",
        ))
```

- [ ] **Step 4: Run, confirm pass**

3 tests OK.

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(validate_member): warn when member.json missing"
```

---

### Task 4: member.json invalid JSON (error severity)

**Files:**
- Modify: `tests/test_validate_member.py`
- Modify: `<LIB>validate_member.py`

- [ ] **Step 1: Failing test**

Append:
```python
    def test_member_json_invalid_yields_error_with_line_col(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "broken"
            folder.mkdir()
            (folder / "member.json").write_text('{ "position": "x"\n  "email": {} }')  # missing comma
            issues = validate_member_folder("broken", folder)
            errors = [i for i in issues if i.severity == "error"]
            self.assertEqual(len(errors), 1)
            self.assertIn("invalid JSON", errors[0].message)
            self.assertIn("line", errors[0].message.lower())
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement — wrap json.load in try/except**

Replace the `member.json` block inside `validate_member_folder`:
```python
    member_json = folder / "member.json"
    if not member_json.exists():
        issues.append(ValidationIssue(
            "warn",
            f"{member_json}: member.json missing — profile will render with defaults.",
        ))
    else:
        try:
            with member_json.open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                "error",
                f"{member_json}: invalid JSON — line {e.lineno}, column {e.colno}: {e.msg}",
            ))
            data = None
        # data is now either a parsed dict or None; schema check uses it in Task 5.
```

- [ ] **Step 4: Run, confirm pass**

4 tests OK.

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(validate_member): error on invalid JSON with line/col"
```

---

### Task 5: Schema type-check (the heart of validation)

**Files:**
- Modify: `tests/test_validate_member.py`
- Modify: `<LIB>validate_member.py`

- [ ] **Step 1: Failing tests (multiple at once for thorough coverage)**

Append:
```python
    def _make_folder(self, tmp, *, member_json_content=None, with_about=False, with_photo=False):
        folder = Path(tmp) / "m"
        folder.mkdir()
        if member_json_content is not None:
            (folder / "member.json").write_text(
                json.dumps(member_json_content), encoding="utf-8"
            )
        if with_about:
            (folder / "about.md").write_text("bio")
        if with_photo:
            (folder / "photo.jpg").write_bytes(b"")
        return folder

    def _good_member_json(self):
        return {
            "position": "Assoc Prof",
            "email": {"ntu": "x@ntu.edu.tw", "preferred": ""},
            "interests": ["A", "B"],
            "links": {
                "scholar": "",
                "orcid": "",
                "linkedin": "",
                "researchgate": "",
                "ntu_scholars": "",
                "office": {"text": "", "url": ""},
            },
            "metaDescription": "",
        }

    def test_fully_valid_member_json_has_no_schema_errors(self):
        import json as _json
        self.maxDiff = None
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(
                tmp, member_json_content=self._good_member_json(),
                with_about=True, with_photo=True,
            )
            issues = validate_member_folder("m", folder)
            errors = [i for i in issues if i.severity == "error"]
            self.assertEqual(errors, [])

    def test_wrong_type_for_position_is_error(self):
        bad = self._good_member_json()
        bad["position"] = None
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(tmp, member_json_content=bad, with_about=True, with_photo=True)
            issues = validate_member_folder("m", folder)
            errors = [i for i in issues if i.severity == "error"]
            self.assertEqual(len(errors), 1)
            self.assertIn("position", errors[0].message)
            self.assertIn("expected string", errors[0].message.lower())

    def test_wrong_nested_type_is_error_with_dotted_path(self):
        bad = self._good_member_json()
        bad["email"]["ntu"] = 42
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(tmp, member_json_content=bad, with_about=True, with_photo=True)
            issues = validate_member_folder("m", folder)
            errors = [i for i in issues if i.severity == "error"]
            self.assertEqual(len(errors), 1)
            self.assertIn("email.ntu", errors[0].message)

    def test_interests_must_be_list_of_strings(self):
        bad = self._good_member_json()
        bad["interests"] = [1, 2]
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(tmp, member_json_content=bad, with_about=True, with_photo=True)
            issues = validate_member_folder("m", folder)
            errors = [i for i in issues if i.severity == "error"]
            self.assertEqual(len(errors), 1)
            self.assertIn("interests[0]", errors[0].message)
```

- [ ] **Step 2: Run, confirm 4 new tests fail**

- [ ] **Step 3: Implement the schema check**

Add to `<LIB>validate_member.py` (above `validate_member_folder`):
```python
# Schema describes member.json shape. Leaves (str, list[str]) are the types;
# branch dicts describe nested structures recursively.
_SCHEMA: dict[str, Any] = {
    "position": str,
    "email": {
        "ntu": str,
        "preferred": str,
    },
    "interests": [str],   # list of strings
    "links": {
        "scholar": str,
        "orcid": str,
        "linkedin": str,
        "researchgate": str,
        "ntu_scholars": str,
        "office": {
            "text": str,
            "url": str,
        },
    },
    "metaDescription": str,
}


def _check_schema(data: Any, schema: Any, path: str) -> list[ValidationIssue]:
    """Recursively validate `data` against `schema`. Returns flat issue list.

    Schema rules:
    - schema is `str` → data must be a `str`
    - schema is `[str]` → data must be a list, every element must be `str`
    - schema is dict → data must be dict; recurse for each key. Keys present
      in schema but absent in data are NOT errors here — empty/missing fields
      are tolerated. (The build's rendering layer hides absent fields.)
    """
    issues: list[ValidationIssue] = []

    if schema is str:
        if not isinstance(data, str):
            issues.append(ValidationIssue(
                "error",
                f"At '{path}': expected string, got {type(data).__name__}",
            ))
    elif isinstance(schema, list) and len(schema) == 1 and schema[0] is str:
        if not isinstance(data, list):
            issues.append(ValidationIssue(
                "error",
                f"At '{path}': expected list of strings, got {type(data).__name__}",
            ))
        else:
            for i, item in enumerate(data):
                if not isinstance(item, str):
                    issues.append(ValidationIssue(
                        "error",
                        f"At '{path}[{i}]': expected string, got {type(item).__name__}",
                    ))
    elif isinstance(schema, dict):
        if not isinstance(data, dict):
            issues.append(ValidationIssue(
                "error",
                f"At '{path}': expected object, got {type(data).__name__}",
            ))
        else:
            for key, subschema in schema.items():
                if key in data:
                    sub_path = f"{path}.{key}" if path else key
                    issues.extend(_check_schema(data[key], subschema, sub_path))

    return issues
```

Update the `else` branch inside `validate_member_folder` (after the `try/except` block):
```python
        if data is not None:
            issues.extend(_check_schema(data, _SCHEMA, path=""))
```

- [ ] **Step 4: Run, confirm 8 tests pass**

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(validate_member): recursive schema check with dotted paths"
```

---

### Task 6: about.md + photo presence warnings

**Files:**
- Modify: `tests/test_validate_member.py`
- Modify: `<LIB>validate_member.py`

- [ ] **Step 1: Failing tests**

Append:
```python
    def test_about_md_missing_yields_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(
                tmp, member_json_content=self._good_member_json(),
                with_about=False, with_photo=True,
            )
            issues = validate_member_folder("m", folder)
            self.assertTrue(any(i.severity == "warn" and "about.md" in i.message for i in issues))

    def test_photo_missing_yields_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(
                tmp, member_json_content=self._good_member_json(),
                with_about=True, with_photo=False,
            )
            issues = validate_member_folder("m", folder)
            self.assertTrue(any(i.severity == "warn" and "photo" in i.message for i in issues))

    def test_photo_can_be_jpg_jpeg_or_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(tmp, member_json_content=self._good_member_json(), with_about=True)
            (folder / "photo.png").write_bytes(b"")
            issues = validate_member_folder("m", folder)
            self.assertFalse(any("photo" in i.message for i in issues))
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement**

Append inside `validate_member_folder` (before `return issues`):
```python
    if not (folder / "about.md").exists():
        issues.append(ValidationIssue(
            "warn",
            f"{folder}/about.md: missing — About section will be hidden on the profile page.",
        ))

    photo_exts = (".jpg", ".jpeg", ".png")
    photos = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in photo_exts and p.stem == "photo"]
    if not photos:
        issues.append(ValidationIssue(
            "warn",
            f"{folder}: no photo.(jpg|jpeg|png) found — default silhouette will be used.",
        ))
```

- [ ] **Step 4: Run, confirm pass**

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(validate_member): warn on missing about.md or photo.{jpg,jpeg,png}"
```

---

### Task 7: URL & email soft-format warnings

**Files:**
- Modify: `tests/test_validate_member.py`
- Modify: `<LIB>validate_member.py`

- [ ] **Step 1: Failing tests**

Append:
```python
    def test_non_http_url_in_links_yields_warning(self):
        bad = self._good_member_json()
        bad["links"]["scholar"] = "scholar.google.com/profile"  # no http(s)://
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(tmp, member_json_content=bad, with_about=True, with_photo=True)
            issues = validate_member_folder("m", folder)
            warns = [i for i in issues if i.severity == "warn" and "scholar" in i.message]
            self.assertEqual(len(warns), 1)
            self.assertIn("http", warns[0].message)

    def test_empty_url_in_links_does_not_warn(self):
        ok = self._good_member_json()
        ok["links"]["scholar"] = ""
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(tmp, member_json_content=ok, with_about=True, with_photo=True)
            issues = validate_member_folder("m", folder)
            self.assertFalse(any("scholar" in i.message for i in issues))

    def test_email_without_at_yields_warning(self):
        bad = self._good_member_json()
        bad["email"]["ntu"] = "notanemail"
        with tempfile.TemporaryDirectory() as tmp:
            folder = self._make_folder(tmp, member_json_content=bad, with_about=True, with_photo=True)
            issues = validate_member_folder("m", folder)
            self.assertTrue(any(i.severity == "warn" and "@" in i.message and "email.ntu" in i.message for i in issues))
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement (extend the schema check post-pass)**

In `<LIB>validate_member.py`, append a helper and call it from `validate_member_folder`:
```python
_URL_LINK_KEYS = ("scholar", "orcid", "linkedin", "researchgate", "ntu_scholars")


def _check_soft_formats(data: dict) -> list[ValidationIssue]:
    """URL / email format warnings. These never fail the build."""
    issues: list[ValidationIssue] = []
    links = data.get("links") or {}

    for key in _URL_LINK_KEYS:
        val = links.get(key)
        if isinstance(val, str) and val and not val.startswith(("http://", "https://")):
            issues.append(ValidationIssue(
                "warn",
                f"links.{key}: '{val}' does not start with http:// or https:// — render will be unchanged but the link may not work.",
            ))

    # office.url is a similar case
    office = links.get("office") or {}
    office_url = office.get("url")
    if isinstance(office_url, str) and office_url and not office_url.startswith(("http://", "https://")):
        issues.append(ValidationIssue(
            "warn",
            f"links.office.url: '{office_url}' does not start with http:// or https://.",
        ))

    email = data.get("email") or {}
    for key in ("ntu", "preferred"):
        val = email.get(key)
        if isinstance(val, str) and val and "@" not in val:
            issues.append(ValidationIssue(
                "warn",
                f"email.{key}: '{val}' missing '@' — does this look right?",
            ))

    return issues
```

In `validate_member_folder`, after the `_check_schema` call, add:
```python
        if data is not None and isinstance(data, dict):
            issues.extend(_check_soft_formats(data))
```

- [ ] **Step 4: Run, confirm pass**

All 11 tests pass.

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(validate_member): soft warnings for non-http URLs and missing-@ emails"
```

---

### Task 8: Integration — wire validator output into a CLI for spot-checking

**Files:**
- Modify: `<LIB>validate_member.py`

- [ ] **Step 1: Add a small `__main__` block so it can be run standalone**

Append to `<LIB>validate_member.py`:
```python
if __name__ == "__main__":
    """Spot-check usage:
        python <LIB>validate_member.py iyunlisahsieh
        python <LIB>validate_member.py iyunlisahsieh contents/members/iyunlisahsieh
    """
    import sys

    if len(sys.argv) < 2:
        print("usage: python validate_member.py <webId> [<folder>]", file=sys.stderr)
        sys.exit(2)

    web_id = sys.argv[1]
    folder = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("contents") / "members" / web_id

    issues = validate_member_folder(web_id, folder)
    if not issues:
        print(f"✓ {folder}: no issues")
        sys.exit(0)

    n_err = sum(1 for i in issues if i.severity == "error")
    for issue in issues:
        sign = "✗" if issue.severity == "error" else "⚠"
        print(f"{sign} {issue.message}")
    sys.exit(1 if n_err else 0)
```

(Reminder: replace `<LIB>` in the `__main__` docstring with the resolved value before committing if PRE_CHORE.)

- [ ] **Step 2: Smoke-test against a real (current) member folder by faking one**

Run:
```bash
mkdir -p /tmp/valtest/iyunlisahsieh
echo '{"position":"x","email":{"ntu":"a@ntu.edu.tw","preferred":""},"interests":[],"links":{"scholar":"","orcid":"","linkedin":"","researchgate":"","ntu_scholars":"","office":{"text":"","url":""}},"metaDescription":""}' > /tmp/valtest/iyunlisahsieh/member.json
echo "bio" > /tmp/valtest/iyunlisahsieh/about.md
touch /tmp/valtest/iyunlisahsieh/photo.jpg
conda run -n E3website python <LIB>validate_member.py iyunlisahsieh /tmp/valtest/iyunlisahsieh
```

Expected: `✓ /tmp/valtest/iyunlisahsieh: no issues` and exit code 0.

- [ ] **Step 3: Commit**

```bash
git commit -am "feat(validate_member): CLI entry point for spot-checking"
```

---

## Phase 2 — Migration script (TDD where possible)

The migration script reads the legacy 22-column Excel and writes the new structure. It is run **once**, then committed alongside its output. Tests cover the pure-function helpers (interest parser, JSON builder, slim-Excel writer) — the end-to-end CLI is smoke-tested in Phase 3.

### Task 9: Scaffold migration script + interest parser (TDD)

**Files:**
- Create: `<LIB>migrate_to_per_member_folders.py`
- Create: `tests/test_migrate_to_per_member_folders.py`

- [ ] **Step 1: Failing test for interest parsing**

Create `tests/test_migrate_to_per_member_folders.py`:
```python
import unittest
from lib.migrate_to_per_member_folders import parse_interests_from_slash_md


class TestParseInterests(unittest.TestCase):
    def test_three_topics_separated_by_blank_lines(self):
        md = "/Smart Grid Modeling\n\n/Energy Management Systems\n\n/Low Carbon Logistics"
        self.assertEqual(
            parse_interests_from_slash_md(md),
            ["Smart Grid Modeling", "Energy Management Systems", "Low Carbon Logistics"],
        )

    def test_no_blank_lines_still_works(self):
        md = "/Topic A\n/Topic B"
        self.assertEqual(parse_interests_from_slash_md(md), ["Topic A", "Topic B"])

    def test_trailing_whitespace_trimmed(self):
        md = "/Topic A   \n/Topic B\t"
        self.assertEqual(parse_interests_from_slash_md(md), ["Topic A", "Topic B"])

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(parse_interests_from_slash_md(""), [])
        self.assertEqual(parse_interests_from_slash_md("\n\n"), [])

    def test_non_slash_lines_ignored(self):
        md = "Random preamble\n/Topic A\nMore noise\n/Topic B"
        self.assertEqual(parse_interests_from_slash_md(md), ["Topic A", "Topic B"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run, confirm fail** — `ModuleNotFoundError`

- [ ] **Step 3: Create the module with the parser**

Create `<LIB>migrate_to_per_member_folders.py`:
```python
"""One-time migration: extract existing per-member content from the legacy
22-column Excel + members-{about,position,interest}/*.md into the new
contents/members/{webId}/ folder structure.

Run from the repo root:
    python <LIB>migrate_to_per_member_folders.py
    python <LIB>migrate_to_per_member_folders.py --force      # overwrite existing folders
    python <LIB>migrate_to_per_member_folders.py --dry-run

Idempotent: re-running without --force will merge new Excel data into
existing per-member folders without overwriting member edits.
"""
from __future__ import annotations


def parse_interests_from_slash_md(md: str) -> list[str]:
    """Parse the existing /Topic A\\n/Topic B format into ['Topic A', 'Topic B']."""
    out: list[str] = []
    for line in (md or "").splitlines():
        s = line.strip()
        if s.startswith("/"):
            out.append(s.lstrip("/").strip())
    return out
```

- [ ] **Step 4: Run, confirm 5 tests pass**

- [ ] **Step 5: Commit**

```bash
git add <LIB>migrate_to_per_member_folders.py tests/test_migrate_to_per_member_folders.py
git commit -m "feat(migrate): scaffold + interest md parser"
```

---

### Task 10: build_member_json from an Excel-row-like dict

**Files:**
- Modify: `tests/test_migrate_to_per_member_folders.py`
- Modify: `<LIB>migrate_to_per_member_folders.py`

- [ ] **Step 1: Failing test**

Append to `tests/test_migrate_to_per_member_folders.py`:
```python
from lib.migrate_to_per_member_folders import build_member_json


class TestBuildMemberJson(unittest.TestCase):
    def _row(self, **overrides):
        # Mirror the legacy column names.
        base = {
            "Preferred Email":      "",
            "NTU Email":            "x@ntu.edu.tw",
            "Position / Education": "Assoc Prof, NTU",
            "Research Interests":   "/Topic A\n/Topic B",
            "metaDescription":      "",
            "Scholar":              "",
            "ORCID":                "0000-0001-2345-6789",
            "LinkedIn":             "",
            "ResearchGate":         "",
            "NTU Scholars":         "",
        }
        base.update(overrides)
        return base

    def test_all_keys_present_even_when_blank(self):
        out = build_member_json(self._row())
        # Top-level keys
        self.assertEqual(set(out.keys()), {"position", "email", "interests", "links", "metaDescription"})
        # Nested keys always present
        self.assertEqual(set(out["email"].keys()), {"ntu", "preferred"})
        self.assertEqual(set(out["links"].keys()), {
            "scholar", "orcid", "linkedin", "researchgate", "ntu_scholars", "office",
        })
        self.assertEqual(set(out["links"]["office"].keys()), {"text", "url"})

    def test_populated_fields_round_trip(self):
        out = build_member_json(self._row())
        self.assertEqual(out["position"], "Assoc Prof, NTU")
        self.assertEqual(out["email"]["ntu"], "x@ntu.edu.tw")
        self.assertEqual(out["email"]["preferred"], "")
        self.assertEqual(out["interests"], ["Topic A", "Topic B"])
        self.assertEqual(out["links"]["orcid"], "0000-0001-2345-6789")
        self.assertEqual(out["links"]["scholar"], "")

    def test_office_text_and_url_pulled_from_separate_columns(self):
        row = self._row()
        row["Office"] = "CERB 601"
        row["Office Map"] = "https://maps.example/abc"
        out = build_member_json(row)
        self.assertEqual(out["links"]["office"], {"text": "CERB 601", "url": "https://maps.example/abc"})

    def test_missing_office_columns_default_to_empty(self):
        out = build_member_json(self._row())
        self.assertEqual(out["links"]["office"], {"text": "", "url": ""})
```

- [ ] **Step 2: Run, confirm fail** — `cannot import build_member_json`

- [ ] **Step 3: Implement**

Append to `<LIB>migrate_to_per_member_folders.py`:
```python
from typing import Mapping, Any


def _s(value: Any) -> str:
    """Coerce Excel cell value → trimmed string, empty when None/blank."""
    if value is None:
        return ""
    return str(value).strip()


def build_member_json(row: Mapping[str, Any]) -> dict[str, Any]:
    """Build the all-keys-present member.json dict from a legacy Excel row.

    `row` is keyed by the legacy 22-column names (e.g. 'NTU Email', 'Scholar').
    Missing columns default to empty values — never raises."""
    return {
        "position": _s(row.get("Position / Education")),
        "email": {
            "ntu":       _s(row.get("NTU Email")),
            "preferred": _s(row.get("Preferred Email")),
        },
        "interests": parse_interests_from_slash_md(_s(row.get("Research Interests"))),
        "links": {
            "scholar":      _s(row.get("Scholar")),
            "orcid":        _s(row.get("ORCID")),
            "linkedin":     _s(row.get("LinkedIn")),
            "researchgate": _s(row.get("ResearchGate")),
            "ntu_scholars": _s(row.get("NTU Scholars")),
            "office": {
                "text": _s(row.get("Office")),
                "url":  _s(row.get("Office Map")),
            },
        },
        "metaDescription": _s(row.get("metaDescription")),
    }
```

- [ ] **Step 4: Run, confirm pass**

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(migrate): build_member_json with all keys always present"
```

---

### Task 11: Write member folder (json + about + photo)

**Files:**
- Modify: `tests/test_migrate_to_per_member_folders.py`
- Modify: `<LIB>migrate_to_per_member_folders.py`

- [ ] **Step 1: Failing test**

Append:
```python
import json
import tempfile
from pathlib import Path
from lib.migrate_to_per_member_folders import write_member_folder


class TestWriteMemberFolder(unittest.TestCase):
    def test_creates_folder_with_json_about_photo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Stage source files the migrator will copy from
            (root / "src_about.md").write_text("# Bio\nHello", encoding="utf-8")
            (root / "src_photo.jpg").write_bytes(b"fake-jpg-bytes")
            member_data = {"position": "x", "email": {"ntu": "", "preferred": ""},
                           "interests": [], "links": {"scholar": "", "orcid": "",
                           "linkedin": "", "researchgate": "", "ntu_scholars": "",
                           "office": {"text": "", "url": ""}}, "metaDescription": ""}

            dest = root / "members" / "ada"
            write_member_folder(
                dest=dest,
                member_json=member_data,
                about_md_src=root / "src_about.md",
                photo_src=root / "src_photo.jpg",
            )

            self.assertTrue((dest / "member.json").exists())
            self.assertTrue((dest / "about.md").exists())
            self.assertTrue((dest / "photo.jpg").exists())
            self.assertEqual(json.loads((dest / "member.json").read_text()), member_data)
            self.assertEqual((dest / "about.md").read_text(encoding="utf-8"), "# Bio\nHello")
            self.assertEqual((dest / "photo.jpg").read_bytes(), b"fake-jpg-bytes")

    def test_skips_missing_about_and_photo_gracefully(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dest = root / "members" / "noaboutphoto"
            write_member_folder(
                dest=dest,
                member_json={"position": "x", "email": {"ntu": "", "preferred": ""},
                             "interests": [], "links": {"scholar": "", "orcid": "",
                             "linkedin": "", "researchgate": "", "ntu_scholars": "",
                             "office": {"text": "", "url": ""}}, "metaDescription": ""},
                about_md_src=None,
                photo_src=None,
            )
            self.assertTrue((dest / "member.json").exists())
            self.assertFalse((dest / "about.md").exists())
            self.assertFalse(list(dest.glob("photo.*")))

    def test_preserves_photo_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "p.png").write_bytes(b"png")
            dest = root / "members" / "m"
            write_member_folder(
                dest=dest,
                member_json={"position": "x", "email": {"ntu": "", "preferred": ""},
                             "interests": [], "links": {"scholar": "", "orcid": "",
                             "linkedin": "", "researchgate": "", "ntu_scholars": "",
                             "office": {"text": "", "url": ""}}, "metaDescription": ""},
                about_md_src=None,
                photo_src=root / "p.png",
            )
            self.assertTrue((dest / "photo.png").exists())
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement**

Append to `<LIB>migrate_to_per_member_folders.py`:
```python
import json as _json
import shutil
from pathlib import Path


def write_member_folder(
    *,
    dest: Path,
    member_json: dict,
    about_md_src: Path | None,
    photo_src: Path | None,
) -> None:
    """Create dest/ and write member.json (+ optionally about.md, photo.{ext}).

    Files are overwritten if they already exist (caller controls --force at
    the CLI level; at the unit level this function is unconditional)."""
    dest.mkdir(parents=True, exist_ok=True)

    (dest / "member.json").write_text(
        _json.dumps(member_json, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if about_md_src is not None and about_md_src.exists():
        (dest / "about.md").write_text(
            about_md_src.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    if photo_src is not None and photo_src.exists():
        ext = photo_src.suffix.lower()
        shutil.copyfile(photo_src, dest / f"photo{ext}")
```

- [ ] **Step 4: Run, confirm pass**

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(migrate): write_member_folder writes json + about + photo"
```

---

### Task 12: Slim-Excel writer

**Files:**
- Modify: `tests/test_migrate_to_per_member_folders.py`
- Modify: `<LIB>migrate_to_per_member_folders.py`

- [ ] **Step 1: Failing test**

Append:
```python
import openpyxl
from lib.migrate_to_per_member_folders import ADMIN_COLUMNS, write_slim_excel


class TestSlimExcel(unittest.TestCase):
    def test_admin_columns_constant_is_eleven(self):
        self.assertEqual(len(ADMIN_COLUMNS), 11)

    def test_writes_only_admin_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Build a 2-row legacy workbook with extra content columns
            legacy = Path(tmp) / "legacy.xlsx"
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Members"
            headers = ["WebID", "Full Name", "NTU Email", "Position / Education",
                       "Website Section", "Admission Year", "Graduated",
                       "Also in Alumni", "Alumni Admission Year",
                       "Current Position", "Batch", "Nickname", "Chinese Name",
                       "Research Interests", "Scholar"]
            ws.append(headers)
            ws.append(["ada", "Ada Lovelace", "a@ntu.edu.tw", "Postdoc",
                       "Full Time", 2024, "FALSE", "FALSE", "",
                       "Postdoc", "2024-FT", "", "", "/x", ""])
            wb.save(legacy)

            slim = Path(tmp) / "slim.xlsx"
            write_slim_excel(legacy, slim)

            wb2 = openpyxl.load_workbook(slim)
            ws2 = wb2["Members"]
            slim_headers = [c.value for c in ws2[1]]
            self.assertEqual(slim_headers, ADMIN_COLUMNS)
            # Row 2 has the admin values in order
            self.assertEqual(ws2["A2"].value, "ada")
            self.assertEqual(ws2["B2"].value, "Ada Lovelace")
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement**

Append to `<LIB>migrate_to_per_member_folders.py`:
```python
ADMIN_COLUMNS: list[str] = [
    "WebID",
    "Full Name",
    "Nickname",
    "Chinese Name",
    "Website Section",
    "Admission Year",
    "Graduated",
    "Also in Alumni",
    "Alumni Admission Year",
    "Current Position",
    "Batch",
]


def write_slim_excel(legacy_path: Path, slim_path: Path) -> None:
    """Read the 22-column legacy workbook; write a new workbook keeping only
    the 11 ADMIN_COLUMNS (in the order defined by that constant)."""
    import openpyxl
    src_wb = openpyxl.load_workbook(legacy_path, data_only=True)
    src_ws = src_wb["Members"]
    src_headers = [c.value for c in src_ws[1]]

    keep_indices = []
    for col in ADMIN_COLUMNS:
        if col not in src_headers:
            raise ValueError(f"Legacy Excel missing required admin column: {col!r}")
        keep_indices.append(src_headers.index(col))

    out_wb = openpyxl.Workbook()
    out_ws = out_wb.active
    out_ws.title = "Members"
    out_ws.append(ADMIN_COLUMNS)
    for row in src_ws.iter_rows(min_row=2, values_only=True):
        out_ws.append([row[i] for i in keep_indices])

    out_wb.save(slim_path)
```

- [ ] **Step 4: Run, confirm pass**

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(migrate): write_slim_excel keeps only the 11 admin columns"
```

---

### Task 13: MEMBER_TEMPLATE skeleton writer

**Files:**
- Modify: `tests/test_migrate_to_per_member_folders.py`
- Modify: `<LIB>migrate_to_per_member_folders.py`

- [ ] **Step 1: Failing test**

Append:
```python
from lib.migrate_to_per_member_folders import write_member_template


class TestMemberTemplate(unittest.TestCase):
    def test_creates_three_files_with_all_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "MEMBER_TEMPLATE"
            write_member_template(dest)
            self.assertTrue((dest / "member.json").exists())
            self.assertTrue((dest / "about.md").exists())
            self.assertTrue((dest / "README.md").exists())

            data = json.loads((dest / "member.json").read_text())
            # All keys present, every leaf empty
            self.assertEqual(data["position"], "")
            self.assertEqual(data["email"]["ntu"], "")
            self.assertEqual(data["email"]["preferred"], "")
            self.assertEqual(data["interests"], [])
            for k in ("scholar", "orcid", "linkedin", "researchgate", "ntu_scholars"):
                self.assertEqual(data["links"][k], "")
            self.assertEqual(data["links"]["office"], {"text": "", "url": ""})

    def test_readme_mentions_member_json_and_about_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "MEMBER_TEMPLATE"
            write_member_template(dest)
            text = (dest / "README.md").read_text(encoding="utf-8")
            self.assertIn("member.json", text)
            self.assertIn("about.md", text)
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement**

Append to `<LIB>migrate_to_per_member_folders.py`:
```python
_EMPTY_MEMBER_JSON: dict = {
    "position": "",
    "email": {"ntu": "", "preferred": ""},
    "interests": [],
    "links": {
        "scholar": "",
        "orcid": "",
        "linkedin": "",
        "researchgate": "",
        "ntu_scholars": "",
        "office": {"text": "", "url": ""},
    },
    "metaDescription": "",
}

_TEMPLATE_ABOUT_MD = """# Your name here

Write your bio in this file. You can use Markdown:

- **bold** with `**bold**`
- *italics* with `*italics*`
- [links](https://example.com) with `[text](url)`

Multiple paragraphs are fine. This is the prose that appears in the "About"
section of your member page.

(Delete this placeholder text and write your bio here.)
"""

_TEMPLATE_README_MD = """# Updating your E3 Center profile

Edit **two files** and send them back to the maintainer:

1. **`member.json`** — your position, emails, interests, profile links.
   - Replace the string values. Don't delete keys or rearrange.
   - Leave any field as `""` to hide it on the website.
   - `interests` is a list — add or remove items as you like (1–5 typical).
2. **`about.md`** — your biographical paragraphs. Plain Markdown:
   - `**bold**`, `*italics*`, `[links](https://example.com)`
   - Blank line = new paragraph
   - `- item` for bullets

Send both files back when done. Do not edit anything in `member-info.xlsx`
— your admin info (name, batch, section) is handled separately.
"""


def write_member_template(dest: Path) -> None:
    """Create dest/ (typically contents/MEMBER_TEMPLATE/) with the three
    skeleton files maintainers send to new members."""
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "member.json").write_text(
        _json.dumps(_EMPTY_MEMBER_JSON, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (dest / "about.md").write_text(_TEMPLATE_ABOUT_MD, encoding="utf-8")
    (dest / "README.md").write_text(_TEMPLATE_README_MD, encoding="utf-8")
```

- [ ] **Step 4: Run, confirm pass**

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(migrate): write_member_template creates the skeleton folder"
```

---

### Task 14: End-to-end migrate() CLI

**Files:**
- Modify: `<LIB>migrate_to_per_member_folders.py`

This task wires the unit-tested helpers into the `main()` CLI. No new unit tests — Phase 3 runs the real migration on the real Excel as the integration test.

- [ ] **Step 1: Implement `main()`**

Append to `<LIB>migrate_to_per_member_folders.py`:
```python
import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One-time migration to per-member folders.")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing contents/members/*/ folders.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen without writing files.")
    args = parser.parse_args(argv)

    repo_root        = Path(".")
    legacy_xlsx      = repo_root / "contents" / "member-info.xlsx"
    archive_xlsx     = repo_root / "contents" / "member-info.legacy.xlsx"
    members_root     = repo_root / "contents" / "members"
    template_root    = repo_root / "contents" / "MEMBER_TEMPLATE"
    old_about_dir    = repo_root / "contents" / "articles" / "members-about"
    old_position_dir = repo_root / "contents" / "articles" / "members-position"
    old_interest_dir = repo_root / "contents" / "articles" / "members-interest"
    old_image_dir    = repo_root / "contents" / "images" / "members"

    if not legacy_xlsx.exists():
        print(f"✗ {legacy_xlsx} does not exist", file=sys.stderr)
        return 2

    if members_root.exists() and any(members_root.iterdir()) and not args.force:
        print(f"✗ {members_root}/ is not empty. Re-run with --force to overwrite.", file=sys.stderr)
        return 2

    import openpyxl
    wb = openpyxl.load_workbook(legacy_xlsx, data_only=True)
    ws = wb["Members"]
    headers = [c.value for c in ws[1]]

    n_processed = 0
    for row_tuple in ws.iter_rows(min_row=2, values_only=True):
        row = dict(zip(headers, row_tuple))
        web_id = _s(row.get("WebID"))
        if not web_id:
            continue

        member_data = build_member_json(row)

        # Position came from a separate markdown file in some cases; prefer
        # the .md file when present so we don't lose its line breaks.
        position_md = old_position_dir / f"{web_id}.md"
        if position_md.exists():
            member_data["position"] = position_md.read_text(encoding="utf-8").strip()

        # Interests were ALSO in a separate .md file historically. If the
        # md exists, prefer its content over the Excel column.
        interest_md = old_interest_dir / f"{web_id}.md"
        if interest_md.exists():
            parsed = parse_interests_from_slash_md(interest_md.read_text(encoding="utf-8"))
            if parsed:
                member_data["interests"] = parsed

        about_md_src = old_about_dir / f"{web_id}.md"
        about_src    = about_md_src if about_md_src.exists() else None

        photo_src: Path | None = None
        for ext in (".jpg", ".jpeg", ".png", ".JPG"):
            cand = old_image_dir / f"{web_id}{ext}"
            if cand.exists():
                photo_src = cand
                break

        dest = members_root / web_id

        if args.dry_run:
            print(f"  would write {dest}/  (about={about_src is not None}, photo={photo_src is not None})")
        else:
            write_member_folder(
                dest=dest,
                member_json=member_data,
                about_md_src=about_src,
                photo_src=photo_src,
            )
            print(f"  ✓ {dest}/")
        n_processed += 1

    if args.dry_run:
        print(f"\n(dry-run) would process {n_processed} members.")
        return 0

    # Slim Excel + archive original
    tmp_slim = legacy_xlsx.with_suffix(".slim.xlsx")
    write_slim_excel(legacy_xlsx, tmp_slim)
    legacy_xlsx.rename(archive_xlsx)
    tmp_slim.rename(legacy_xlsx)
    print(f"  ✓ wrote slim {legacy_xlsx}")
    print(f"  ✓ archived original → {archive_xlsx}")

    # Template skeleton
    write_member_template(template_root)
    print(f"  ✓ wrote {template_root}/")

    print(f"\nDone. Processed {n_processed} members.")
    print("\nNext steps (manual):")
    print("  - Inspect a few migrated folders (e.g. contents/members/iyunlisahsieh/)")
    print("  - Run: python build.py  (should succeed with at most warnings)")
    print("  - diff -r /tmp/docs.before docs   (zero diffs expected)")
    print("  - git rm -r contents/articles/members-{about,position,interest}/")
    print("                contents/structures/members/ contents/images/members/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Re-run the full test suite to confirm no regressions**

Run: `conda run -n E3website python -m unittest -v`

Expected: all tests pass (validator + migration + existing seo_helpers).

- [ ] **Step 3: Commit**

```bash
git commit -am "feat(migrate): main() CLI wires helpers + writes slim Excel + archives legacy"
```

---

## Phase 3 — Run the migration

This phase actually creates the per-member folders. No tests — just running the script and verifying.

### Task 15: Run migration, eyeball results

**Files:**
- (will create) `contents/members/*/{member.json, about.md, photo.{ext}}`
- (will create) `contents/MEMBER_TEMPLATE/{member.json, about.md, README.md}`
- (will create) `contents/member-info.legacy.xlsx` (rename of original)
- (will rewrite) `contents/member-info.xlsx` (slim, 11 columns)

- [ ] **Step 1: Dry-run first**

Run:
```bash
conda run -n E3website python <LIB>migrate_to_per_member_folders.py --dry-run
```

Expected: prints `would write contents/members/{webId}/  ...` for each of the ~26 rows, then `(dry-run) would process 26 members.` No files written.

- [ ] **Step 2: Real run**

Run:
```bash
conda run -n E3website python <LIB>migrate_to_per_member_folders.py
```

Expected: ~26 lines of `✓ contents/members/{webId}/`, then the slim Excel + archive + template confirmations, then `Done. Processed 26 members.`

- [ ] **Step 3: Inspect three migrated folders**

Run:
```bash
ls -la contents/members/iyunlisahsieh/
cat contents/members/iyunlisahsieh/member.json
head -20 contents/members/iyunlisahsieh/about.md
```

Confirm visually: all keys present in `member.json`, `about.md` matches the existing `contents/articles/members-about/iyunlisahsieh.md` content, `photo.jpg` exists.

Repeat for one PhD student and one alumni member (pick from the listing).

- [ ] **Step 4: Confirm slim Excel has 11 columns**

Run:
```bash
conda run -n E3website python -c "
import openpyxl
wb = openpyxl.load_workbook('contents/member-info.xlsx', data_only=True)
ws = wb['Members']
print([c.value for c in ws[1]])
print('rows:', ws.max_row - 1)
"
```

Expected: list of exactly 11 admin column names. Row count matches dry-run.

- [ ] **Step 5: Stage but don't commit yet**

```bash
git add contents/members/ contents/MEMBER_TEMPLATE/ contents/member-info.xlsx contents/member-info.legacy.xlsx
git status --short
```

Confirm: ~80–110 new files staged (member.json/about.md/photo × 26 members + template skeleton + Excel pair). No deletions yet — those come in Phase 5.

---

## Phase 4 — Refactor `excel_to_content.py` + `build.py`

This is the riskiest phase. Build pipeline runs end-to-end; small refactor + snapshot-diff after each change.

### Task 16: Capture pre-refactor `docs/` snapshot

**Files:** (none modified)

- [ ] **Step 1: Ensure migration files are still staged, but the OLD pipeline still works (legacy `articles/members-*` and `structures/members/` directories still exist)**

```bash
git status -s | grep "contents/articles/members" | head -3
```

Expected: no output (those files are unmodified, unstaged).

- [ ] **Step 2: Build now and snapshot**

```bash
conda run -n E3website python build.py
rm -rf /tmp/docs.snapshot
cp -r docs /tmp/docs.snapshot
```

Expected: `Build complete!`. The snapshot is our golden file.

---

### Task 17: Refactor `excel_to_content.py` to read from per-member folders

**Files:**
- Modify: `<LIB>excel_to_content.py`

The current `<LIB>excel_to_content.py` writes 4 files per member (1 JSON + 3 MDs). After this refactor it writes ZERO per-member files; instead the merger reconstructs the legacy in-memory shape that `build.py` already consumes.

- [ ] **Step 1: Read the existing file to locate the relevant block**

Run:
```bash
grep -n "members-about\|members-position\|members-interest\|structures/members/\|md_written\|json_written" <LIB>excel_to_content.py
```

Note the line ranges of:
- the per-member JSON write loop
- the markdown file writes
- the `members-by-section` aggregation (this stays)

- [ ] **Step 2: Replace the per-member writes with folder reads + in-memory dict**

In `<LIB>excel_to_content.py`, find the section that writes `contents/structures/members/{web_id}.json` and the three per-member `.md` files. Replace those writes with:

```python
# --- New: read content fields from contents/members/{web_id}/ --------
from pathlib import Path
import json as _json

_members_root = Path("contents") / "members"
content_folder = _members_root / web_id

# Defaults — used when the folder is incomplete.
content = {
    "position": "",
    "email": {"ntu": "", "preferred": ""},
    "interests": [],
    "links": {
        "scholar": "", "orcid": "", "linkedin": "",
        "researchgate": "", "ntu_scholars": "",
        "office": {"text": "", "url": ""},
    },
    "metaDescription": "",
}

member_json_path = content_folder / "member.json"
if member_json_path.exists():
    try:
        content.update(_json.loads(member_json_path.read_text(encoding="utf-8")))
    except _json.JSONDecodeError as e:
        print(f"  ✗ {member_json_path}: invalid JSON — line {e.lineno}, col {e.colno}: {e.msg}",
              file=__import__("sys").stderr)
        raise  # build must fail
```

Then, where the old code constructed the per-member dict (the one that became `contents/structures/members/{web_id}.json`), substitute fields from `content` instead of from individual Excel cells:

```python
# OLD: email     = str(col(row, 'Preferred Email')      or '').strip()
# OLD: ntu_email = str(col(row, 'NTU Email')            or '').strip()
# OLD: position  = str(col(row, 'Position / Education') or '').strip()
# OLD: interests = str(col(row, 'Research Interests')   or '').strip()
# NEW:
email     = content["email"]["preferred"]
ntu_email = content["email"]["ntu"]
position  = content["position"]
interests_list = content["interests"]   # already a list of strings
meta_description = (content["metaDescription"] or None)
```

Where the old code read the link URL columns (`Scholar`, `ORCID`, etc.) via `build_profile_links(row, headers)`, substitute reading from `content["links"]`. Adapt `build_profile_links` (or its caller) to accept a links dict instead of a row.

For the `interests` rendering path (the old code wrote a markdown file like `/Smart Grid Modeling\n/...`), feed the in-memory list directly into the existing rendering routine. If the old code reads `interest_content` later in `build.py`, the merger needs to construct an equivalent string. Audit where `interest_content` is consumed:

```bash
grep -rn "interest_content" build.py templates/
```

The simplest approach: keep `interest_content` as the rendered HTML string (the same shape templates expect), produced by passing the new `content["interests"]` list through `markdown.markdown`. Example:

```python
interest_md = "\n\n".join(f"/{topic}" for topic in content["interests"])
interest_content = markdown.markdown(interest_md, extensions=["md_in_html"])
```

Finally, **delete** the lines that wrote files to disk:

```python
# DELETED:
# with open(json_path, 'w', ...) as f: json.dump(member_json, f, ...)
# write_md(about_path, about); write_md(position_path, position); ...
```

The `members.json` write (the section-grouped listing) stays — that's a side-product of Excel iteration and still gets used by the members listing page.

- [ ] **Step 3: Update `build.py` to read `about.md` from the new location**

In `build.py` find where `about_content[...]` is populated. The current code walks `contents/articles/` and reads every `.md`. After the refactor, `members-about/` no longer exists — about content lives in `contents/members/{webId}/about.md`. Adapt:

```bash
grep -n "members-about\|members-position\|members-interest" build.py
```

Replace the walks of those legacy directories with reads from `contents/members/{webId}/about.md`. Inject the rendered HTML under the same `about_content[...]` key the templates already use (likely keyed by relative path like `members-about/iyunlisahsieh`) — easiest fix is to construct a synthetic key per member: `about_content[f"members-about/{web_id}"] = markdown.markdown(...)`. This preserves the template's existing `about_content[section['content']]` lookup.

- [ ] **Step 4: Wire the validator into the build**

In `<LIB>excel_to_content.py`, before the dict construction, call the validator and crash on errors:

```python
from <LIB>validate_member import validate_member_folder

issues = validate_member_folder(web_id, content_folder)
errors = [i for i in issues if i.severity == "error"]
if errors:
    for e in errors:
        print(f"  ✗ {e.message}", file=__import__("sys").stderr)
    raise SystemExit(2)
for i in issues:
    if i.severity == "warn":
        print(f"  ⚠ {i.message}")
```

(`<LIB>` here is the import form — substitute per the table at the top: POST_CHORE → `lib.`, PRE_CHORE → empty.)

- [ ] **Step 5: Run the build, fix until green**

```bash
conda run -n E3website python build.py
```

Expected: `Build complete!` (possibly with `⚠` warnings for members without photos or about.md).

If it fails: read the error, fix the merger, re-run. Common failures:
- KeyError on `pageContent['links']` — the merger needs to assemble the links list in the legacy shape (icons + URLs) from `content["links"]`. Compare against an old `structures/members/{id}.json` for the expected shape.
- KeyError on `pageContent['aboutSection']` — the merger needs to emit the legacy `[{sectionTitle: 'About', content: 'members-about/{webId}'}]` list shape.

- [ ] **Step 6: Diff `docs/` vs the snapshot**

```bash
diff -r /tmp/docs.snapshot docs | head -100
```

Expected: minimal diffs — only date/time changes in sitemap.xml, identical HTML elsewhere. Substantial HTML diffs = a regression to fix before commit.

If diffs are clean, proceed. If not, iterate Step 5 → Step 6.

- [ ] **Step 7: Commit refactor + migration together**

The refactor and the migration are useless without each other. Single commit covers both:

```bash
git add <LIB>excel_to_content.py build.py
git add contents/members/ contents/MEMBER_TEMPLATE/ contents/member-info.xlsx contents/member-info.legacy.xlsx
git commit -m "refactor(content): migrate per-member data into contents/members/{id}/

- excel_to_content.py now reads content fields (position, email, interests,
  links, bio) from contents/members/{webId}/member.json + about.md and
  merges them with admin fields from the slim 11-column Excel.
- Validation via validate_member_folder runs before merge; build fails on
  invalid JSON or schema mismatch, warns on missing optional files.
- One-time migration script extracted the existing 22-col Excel + old
  per-member MDs into the new structure (26 members + MEMBER_TEMPLATE
  skeleton + member-info.legacy.xlsx archive).
- Rendering verified byte-identical against pre-refactor docs/ snapshot."
```

---

### Task 18: Move image processing to read from per-member folders

**Files:**
- Modify: `build.py` (image processing step, currently iterates `contents/images/members/`)

- [ ] **Step 1: Locate the image processing block**

Run:
```bash
grep -n "members.*img_sizes\|contents/images/members\|find_image" build.py <LIB>excel_to_content.py
```

The image pipeline currently iterates `contents/images/members/*.{jpg,png}` and writes `docs/assets/members/{webId}-{N}w.webp`. After this task it iterates `contents/members/*/photo.*` and writes the same destination paths (so existing HTML srcset references continue to work).

- [ ] **Step 2: Update the iteration**

Replace:
```python
# OLD (paraphrased):
for img in (Path("contents/images/members")).iterdir():
    web_id = img.stem
    ...
```

With:
```python
# NEW:
for member_dir in (Path("contents/members")).iterdir():
    if not member_dir.is_dir():
        continue
    photos = [p for p in member_dir.iterdir()
              if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".JPG")
              and p.stem == "photo"]
    if not photos:
        continue
    img = photos[0]
    web_id = member_dir.name
    # … existing srcset-generation code unchanged …
```

If `excel_to_content.py` has its own `find_image()` helper (it does), update that too:

```python
def find_image(web_id: str) -> str | None:
    folder = Path("contents/members") / web_id
    for ext in (".jpg", ".jpeg", ".png", ".JPG"):
        cand = folder / f"photo{ext}"
        if cand.exists():
            return f"/assets/members/{web_id}{ext.lower()}"
    return None
```

(Output path string returned from `find_image` should match what it returned before — the templates use `imgPath.split('.')[0]` so the `.lower()` normalization is fine.)

- [ ] **Step 3: Run build + diff**

```bash
conda run -n E3website python build.py
diff -r /tmp/docs.snapshot docs | head -100
```

Expected: still zero unexpected diffs. The WebP outputs in `docs/assets/members/` should match byte-for-byte (the source images are the same files, just at new paths).

- [ ] **Step 4: Commit**

```bash
git add build.py <LIB>excel_to_content.py
git commit -m "refactor(images): read member photos from contents/members/{id}/photo.*

Output paths in docs/assets/members/ are unchanged so existing HTML
srcset references continue to work without template updates."
```

---

## Phase 5 — Cleanup + docs

### Task 19: Delete stale directories

**Files:**
- Delete: `contents/articles/members-about/` (entire dir)
- Delete: `contents/articles/members-position/` (entire dir)
- Delete: `contents/articles/members-interest/` (entire dir)
- Delete: `contents/structures/members/` (entire dir)
- Delete: `contents/images/members/` (entire dir)

- [ ] **Step 1: Confirm none of these are still read by the build**

Run:
```bash
grep -rn "members-about\|members-position\|members-interest\|contents/structures/members\|contents/images/members" build.py <LIB>*.py templates/ static/
```

Expected: only the matches in the migration script (intentional — that's the source for the migration). No matches in `build.py`, `<LIB>excel_to_content.py`, templates, or static.

If the grep returns any match in build.py / excel_to_content.py / templates that ISN'T inside the migration script, fix it before deleting.

- [ ] **Step 2: `git rm -r` the directories**

```bash
git rm -r contents/articles/members-about/
git rm -r contents/articles/members-position/
git rm -r contents/articles/members-interest/
git rm -r contents/structures/members/
git rm -r contents/images/members/
```

- [ ] **Step 3: Build + diff once more**

```bash
conda run -n E3website python build.py
diff -r /tmp/docs.snapshot docs | head -100
```

Expected: still zero unexpected diffs. The build no longer reads the deleted dirs, so the rendering output is unchanged.

- [ ] **Step 4: Commit**

```bash
git commit -m "chore: delete legacy per-member dirs now that contents/members/ is the source

- contents/articles/members-about/
- contents/articles/members-position/
- contents/articles/members-interest/
- contents/structures/members/
- contents/images/members/

Build still renders byte-identical output (snapshot diff confirmed)."
```

---

### Task 20: Update STRUCTURE.md

**Files:**
- Modify: `STRUCTURE.md`

- [ ] **Step 1: Read current contents**

Run: `cat STRUCTURE.md | head -60`

- [ ] **Step 2: Rewrite the directory tree + build steps to reflect the new layout**

The `contents/` tree section should now show:
```
contents/
├── member-info.xlsx           # ★ Admin roster — 11 columns, edit for new/graduated/section changes
├── member-info.legacy.xlsx    # Original 22-column file, reference only
├── MEMBER_TEMPLATE/           # Skeleton you copy when adding a new member
│   ├── member.json            # All-empty schema for member to fill in
│   ├── about.md               # Bio prose placeholder
│   └── README.md              # Instructions for the member
├── members/                   # One folder per member, keyed by webId
│   └── {webId}/
│       ├── member.json        # Content fields — position, emails, interests, links
│       ├── about.md           # Bio prose with full Markdown
│       └── photo.{jpg,png}    # Headshot, auto-converted to WebP
├── structures/
│   ├── pages.json
│   ├── publications.json
│   ├── research.json
│   ├── about.json
│   ├── contact.json
│   ├── news.json
│   ├── group-life.json
│   └── videos.json
├── articles/
│   ├── about.md
│   ├── contact.md
│   └── news/
└── images/
    ├── research/
    ├── group-life/
    └── news/
```

Remove the lines about `articles/members-{about,position,interest}/` and `structures/members/` AUTO-GENERATED notes. Replace the "Build Process" section's step describing the per-member JSON/MD generation with the new merge step:

```
1. Run lib/excel_to_content.py
   - Read admin columns from contents/member-info.xlsx
   - For each row: read contents/members/{webId}/{member.json, about.md}
   - Validate JSON schema (lib/validate_member.py)
   - Build the in-memory per-member dict the templates consume
   - Write contents/structures/members.json (the section-grouped listing)
```

- [ ] **Step 3: Commit**

```bash
git add STRUCTURE.md
git commit -m "docs(STRUCTURE): describe contents/members/{webId}/ layout and merge build step"
```

---

### Task 21: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Find the data-flow diagram + build-steps section**

Run: `grep -n "Data flows\|excel_to_content\|members-about\|members-position\|members-interest" CLAUDE.md`

- [ ] **Step 2: Update the data-flow block**

Replace the data-flow ASCII block with:
```
contents/member-info.xlsx       ← roster (admin: webId, names, section, batch, graduated)
        ↓
contents/members/{webId}/       ← per-member content folder
        ├── member.json         ← position, emails, interests, links
        ├── about.md            ← bio prose with Markdown
        └── photo.{jpg,png}     ← headshot
        ↓
<LIB>excel_to_content.py        ← merges admin + content into per-member dict
<LIB>validate_member.py         ← schema check, error on malformed JSON
        ↓
templates/pages/member/member.html  ← receives merged dict (unchanged shape)
        ↓
docs/{member.pageLink}/index.html
```

Update step 1 of the build process:
```
1. lib/excel_to_content.py — reads slim Excel + per-member folders,
   validates JSON, writes only contents/structures/members.json (the
   section-grouped listing). Per-member JSONs are NO LONGER generated;
   they are read directly from disk.
```

Add a new "Adding/updating a member" section reflecting the new workflow (copy folder, send to member, paste back).

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE): new data flow + per-member folder workflow"
```

---

### Task 22: Update CONTRIBUTING.md

**Files:**
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Find the member-related instructions**

Run: `grep -n "members-about\|members-position\|members-interest\|excel_to_content\|adding a member\|Adding a Member" CONTRIBUTING.md`

- [ ] **Step 2: Rewrite the "Adding a member" section**

Replace any mention of `excel_to_content.py` generating the per-member files with the new flow:

```
## Adding or updating a member

For an EXISTING member:
  1. cp -r contents/members/{webId} /tmp/pkg/
  2. Email the folder to the member (zip first).
  3. Member edits member.json + about.md, sends back.
  4. cp -r /tmp/pkg/{webId}/* contents/members/{webId}/
  5. git diff to review; commit; push.

For a NEW member:
  1. cp -r contents/MEMBER_TEMPLATE /tmp/pkg/
  2. Add a new row to contents/member-info.xlsx with WebID, Full Name,
     Nickname (optional), Chinese Name, Website Section, Admission Year,
     Graduated=FALSE, etc. (11 admin columns).
  3. Email the template folder to the new member.
  4. When returned: mv /tmp/pkg/{webId}/ contents/members/{webId}/
  5. python build.py → confirm warnings are only "expected"
  6. Commit, push.

DO NOT edit:
  - contents/member-info.legacy.xlsx (read-only archive)
  - contents/structures/members.json (auto-generated)
```

- [ ] **Step 3: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs(CONTRIBUTING): document per-member folder workflow"
```

---

## Phase 6 — Final verification + PR

### Task 23: Final smoke tests

**Files:** (none)

- [ ] **Step 1: Full build**

```bash
conda run -n E3website python build.py 2>&1 | tail -10
```

Expected: `Build complete!`, no `✗ ERROR` lines (warnings ⚠ for any incomplete members are acceptable).

- [ ] **Step 2: Full test suite**

```bash
conda run -n E3website python -m unittest -v 2>&1 | tail -20
```

Expected: all tests pass (existing `test_seo_helpers` + new `test_validate_member` + new `test_migrate_to_per_member_folders`).

- [ ] **Step 3: Verify a member page renders the same**

Compare two specific pages between snapshot and current:

```bash
diff /tmp/docs.snapshot/members/iyunlisahsieh/index.html docs/members/iyunlisahsieh/index.html | head -20
diff /tmp/docs.snapshot/members/junweiding/index.html docs/members/junweiding/index.html | head -20
diff /tmp/docs.snapshot/index.html docs/index.html | head -20
```

Expected: empty diffs (or only updated_time timestamps).

- [ ] **Step 4: Live-edit smoke test**

```bash
# Make a trivial edit to confirm the new pipeline actually picks it up
echo "" >> contents/members/iyunlisahsieh/about.md
echo "[Test paragraph — remove before commit.]" >> contents/members/iyunlisahsieh/about.md
conda run -n E3website python build.py
grep "Test paragraph" docs/members/iyunlisahsieh/index.html
# Undo
git checkout contents/members/iyunlisahsieh/about.md
```

Expected: the grep finds the test string in the rendered HTML, then the checkout reverts the file.

- [ ] **Step 5: Validation smoke test**

```bash
# Inject a deliberate syntax error
cp contents/members/iyunlisahsieh/member.json /tmp/m.json.bak
echo "}" >> contents/members/iyunlisahsieh/member.json
conda run -n E3website python build.py 2>&1 | tail -5
# Restore
mv /tmp/m.json.bak contents/members/iyunlisahsieh/member.json
```

Expected: build exits non-zero with a `✗ contents/members/iyunlisahsieh/member.json: invalid JSON — line X, col Y` message. Then the restore puts the file back.

If the build succeeded despite the broken JSON, the validator wiring (Task 17 Step 4) is incomplete — go back and fix.

---

### Task 24: Push and open PR

**Files:** (none)

- [ ] **Step 1: Push the branch**

```bash
git push -u origin feat/member-content-restructure
```

- [ ] **Step 2: Open the PR via `gh pr create`**

```bash
gh pr create --title "feat: per-member content folders (contents/members/{webId}/)" \
  --body "$(cat <<'EOF'
## Summary

Restructures \`contents/\` so each member's data lives in a self-contained folder:

\`\`\`
contents/members/{webId}/
├── member.json    ← content fields (position, emails, interests, links)
├── about.md       ← bio prose with Markdown
└── photo.{ext}    ← headshot
\`\`\`

Excel keeps the 11 admin columns (WebID, names, section, batch, graduated, current position) and acts as a roster. The build merges admin + content into the per-member dict templates already consume — templates are unchanged.

### Why

Members can't edit Excel cells effectively (no Markdown, no diff). The "download folder → send to member → paste back" workflow gives them a friendly text editor + the JSON file already has every key present so they only change values.

## What changed

- New \`lib/validate_member.py\`: schema check with helpful error messages.
- New \`lib/migrate_to_per_member_folders.py\`: one-time committed migration.
- Refactored \`lib/excel_to_content.py\`: no longer generates per-member JSON/MD; reads from \`contents/members/{webId}/\` and merges with Excel admin fields.
- Refactored \`build.py\` image step: iterates \`contents/members/*/photo.*\` (output paths unchanged).
- Deleted: \`contents/articles/members-{about,position,interest}/\`, \`contents/structures/members/\`, \`contents/images/members/\` (now sourced from per-member folders).
- New \`contents/MEMBER_TEMPLATE/\`: skeleton for new members.
- Old Excel preserved as \`contents/member-info.legacy.xlsx\` (read-only).

## Spec + plan

- Design spec: \`superpowers/specs/2026-05-13-contents-member-restructure-design.md\`
- Implementation plan: \`superpowers/plans/2026-05-13-contents-member-restructure.md\`

## Test plan

- [ ] CI build succeeds on this PR.
- [ ] \`python -m unittest -v\` runs all suites green.
- [ ] Spot-check 3 migrated member pages render identically to pre-migration (\`/members/iyunlisahsieh/\`, one PhD, one alumni).
- [ ] Edit one \`about.md\` locally, rebuild, confirm the page reflects the change.
- [ ] Introduce a deliberate JSON syntax error in one \`member.json\`, confirm build fails with line/col message.
- [ ] \`/members/\` listing page still groups by section correctly.
- [ ] Homepage members section still renders.
- [ ] Publications attribution still bolds member names correctly.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 3: Verify PR opened**

```bash
gh pr view --json url,state -q .url
```

Expected: a URL to the new PR.

---

## File structure overview (post-implementation)

```
NTU-E3-Center.github.io/
├── build.py                                 # (modified) image step uses per-member folders
├── <LIB>excel_to_content.py                 # (refactored) merges Excel + per-member content
├── <LIB>validate_member.py                  # (NEW) JSON schema + checks
├── <LIB>migrate_to_per_member_folders.py    # (NEW, one-time)
├── contents/
│   ├── member-info.xlsx                     # (REGENERATED) 11 admin columns
│   ├── member-info.legacy.xlsx              # (NEW) archive of original 22-col file
│   ├── MEMBER_TEMPLATE/                     # (NEW) skeleton for new members
│   │   ├── member.json
│   │   ├── about.md
│   │   └── README.md
│   ├── members/                             # (NEW) per-member folders
│   │   ├── iyunlisahsieh/
│   │   ├── junweiding/
│   │   └── … (~26 folders total)
│   ├── articles/
│   │   ├── about.md                         # (unchanged)
│   │   ├── contact.md                       # (unchanged)
│   │   └── news/                            # (unchanged)
│   │   # DELETED: members-{about,position,interest}/
│   ├── structures/
│   │   ├── pages.json                       # (unchanged)
│   │   ├── members.json                     # (still auto-generated — section listing)
│   │   ├── publications.json                # (unchanged)
│   │   └── …                                # (other JSONs unchanged)
│   │   # DELETED: members/ (per-member JSONs)
│   └── images/
│       ├── research/                        # (unchanged)
│       ├── group-life/                      # (unchanged)
│       └── news/                            # (unchanged)
│       # DELETED: members/ (now inside contents/members/*/photo.*)
├── tests/
│   ├── test_seo_helpers.py                  # (unchanged)
│   ├── test_validate_member.py              # (NEW)
│   └── test_migrate_to_per_member_folders.py  # (NEW)
├── STRUCTURE.md                             # (updated tree + steps)
├── CLAUDE.md                                # (updated data flow + workflow)
└── CONTRIBUTING.md                          # (updated "Adding a member")
```

---

## Self-review (writer's pass)

**Spec coverage:**
- §1 motivation, §2 decisions — captured in plan goals/architecture ✓
- §3 directory layout — Task 15 produces it; Task 20 documents it ✓
- §4 Excel column trim — Task 12 implements + tests ✓
- §5 member.json schema — Task 5 + Task 11 test cases match the spec table ✓
- §6 about.md rules — Task 11 implements; Task 17 wires into build ✓
- §7 member workflow — Task 22 documents in CONTRIBUTING ✓
- §8 build.py changes — Tasks 17 + 18 ✓
- §9 validation — Tasks 1–8 ✓
- §10 migration script — Tasks 9–15 ✓
- §11 out of scope — preserved (no work added for these) ✓
- §12 risks — Task 23 smoke tests cover each ✓
- §13 acceptance criteria — Task 23 step-by-step ✓
- §14 handoff — this plan IS the handoff ✓

**Placeholder scan:** No "TBD" / "implement later" / unreferenced types. The `<LIB>` placeholder is resolved at Task 0 and substituted consistently.

**Type consistency:** `ValidationIssue(severity, message)` used identically across Tasks 1–8. `build_member_json(row) → dict` signature stable across Tasks 10–14. CLI flags (`--force`, `--dry-run`) match between Task 14 and Task 15.

**Implementation independence:** Tasks 1–8 (validator) and Tasks 9–13 (migration helpers) can be done in any order — they don't reference each other. Tasks 14–15 depend on 9–13. Tasks 17–18 depend on 15. Task 19 depends on 17–18 (or rendering changes need rollback). Documentation Tasks 20–22 can be parallelized.
