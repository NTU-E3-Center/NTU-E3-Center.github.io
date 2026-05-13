import unittest
from pathlib import Path
import tempfile
import json

from validate_member import validate_member_folder, ValidationIssue


class TestValidateMemberFolder(unittest.TestCase):
    def test_returns_list_of_validation_issues(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "missing"
            issues = validate_member_folder("nobody", folder)
            self.assertIsInstance(issues, list)
            self.assertTrue(all(isinstance(i, ValidationIssue) for i in issues))

    def test_folder_missing_yields_one_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "nonexistent"
            issues = validate_member_folder("nobody", folder)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0].severity, "warn")
            self.assertIn("folder missing", issues[0].message)

    def test_member_json_missing_yields_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "empty"
            folder.mkdir()
            issues = validate_member_folder("empty", folder)
            severities = [(i.severity, "member.json" in i.message) for i in issues]
            self.assertIn(("warn", True), severities)

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


if __name__ == "__main__":
    unittest.main()
