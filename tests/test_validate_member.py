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
            # One error per non-string element — both items fail the check.
            self.assertEqual(len(errors), 2)
            self.assertIn("interests[0]", errors[0].message)
            self.assertIn("interests[1]", errors[1].message)


if __name__ == "__main__":
    unittest.main()
