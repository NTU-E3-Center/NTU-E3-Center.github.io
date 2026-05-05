import unittest
from seo_helpers import generate_meta_description


class TestGenerateMetaDescription(unittest.TestCase):
    def test_returns_override_when_provided(self):
        result = generate_meta_description(
            "Director of E3 Center, working on hydrogen.",
            "fallback text",
        )
        self.assertEqual(result, "Director of E3 Center, working on hydrogen.")

    def test_uses_first_nonempty_fallback(self):
        result = generate_meta_description(None, "", "  ", "real fallback content here")
        self.assertEqual(result, "real fallback content here")

    def test_truncates_to_max_chars_at_word_boundary(self):
        long = " ".join(["word"] * 100)  # 499 chars
        result = generate_meta_description(None, long, max_chars=50)
        self.assertLessEqual(len(result), 50)
        self.assertFalse(result.endswith("wo"), "should not cut mid-word")

    def test_preserves_short_text_unchanged(self):
        result = generate_meta_description(None, "short text", max_chars=160)
        self.assertEqual(result, "short text")

    def test_returns_empty_string_when_all_sources_empty(self):
        self.assertEqual(generate_meta_description(None, "", None), "")

    def test_collapses_whitespace(self):
        result = generate_meta_description(None, "line1\n\n  line2  \tline3")
        self.assertEqual(result, "line1 line2 line3")
