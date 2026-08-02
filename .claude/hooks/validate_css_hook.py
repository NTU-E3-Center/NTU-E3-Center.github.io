#!/usr/bin/env python3
"""PostToolUse hook: run validate_design_tokens.py after any static/css edit.

Reads the hook payload from stdin. When the edited file is a CSS file under
static/css/, runs the design-token validator from the repo root; on failure
the report goes to stderr with exit code 2, which feeds the violations back
to Claude to fix immediately. Any other file exits 0 silently.
"""
import json
import os
import subprocess
import sys


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    path = (payload.get("tool_input") or {}).get("file_path") or ""
    path = path.replace("\\", "/")
    if not path.endswith(".css"):
        return 0
    if "/static/css/" not in path and not path.startswith("static/css/"):
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    result = subprocess.run(
        [sys.executable, "validate_design_tokens.py"],
        capture_output=True, text=True, cwd=root)
    if result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
