import json
import tempfile
import unittest
from pathlib import Path

import openpyxl

from migrate_to_per_member_folders import (
    parse_interests_from_slash_md,
    build_member_json,
    write_member_folder,
    write_slim_excel,
    write_member_template,
    ADMIN_COLUMNS,
)


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


class TestBuildMemberJson(unittest.TestCase):
    def _row(self, **overrides):
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
        self.assertEqual(set(out.keys()), {"position", "email", "interests", "links", "metaDescription"})
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


def _empty_member_dict():
    return {
        "position": "x",
        "email": {"ntu": "", "preferred": ""},
        "interests": [],
        "links": {
            "scholar": "", "orcid": "", "linkedin": "",
            "researchgate": "", "ntu_scholars": "",
            "office": {"text": "", "url": ""},
        },
        "metaDescription": "",
    }


class TestWriteMemberFolder(unittest.TestCase):
    def test_creates_folder_with_json_about_photo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src_about.md").write_text("# Bio\nHello", encoding="utf-8")
            (root / "src_photo.jpg").write_bytes(b"fake-jpg-bytes")
            member_data = _empty_member_dict()

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
                member_json=_empty_member_dict(),
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
                member_json=_empty_member_dict(),
                about_md_src=None,
                photo_src=root / "p.png",
            )
            self.assertTrue((dest / "photo.png").exists())


class TestSlimExcel(unittest.TestCase):
    def test_admin_columns_constant_is_eleven(self):
        self.assertEqual(len(ADMIN_COLUMNS), 11)

    def test_writes_only_admin_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
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
            self.assertEqual(ws2["A2"].value, "ada")
            self.assertEqual(ws2["B2"].value, "Ada Lovelace")


class TestMemberTemplate(unittest.TestCase):
    def test_creates_three_files_with_all_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "MEMBER_TEMPLATE"
            write_member_template(dest)
            self.assertTrue((dest / "member.json").exists())
            self.assertTrue((dest / "about.md").exists())
            self.assertTrue((dest / "README.md").exists())

            data = json.loads((dest / "member.json").read_text())
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


if __name__ == "__main__":
    unittest.main()
