import unittest
from migrate_to_per_member_folders import parse_interests_from_slash_md


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
