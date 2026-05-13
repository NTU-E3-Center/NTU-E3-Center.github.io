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


if __name__ == "__main__":
    unittest.main()
