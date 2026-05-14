import unittest
from migrate_to_per_member_folders import (
    parse_interests_from_slash_md,
    build_member_json,
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


if __name__ == "__main__":
    unittest.main()
