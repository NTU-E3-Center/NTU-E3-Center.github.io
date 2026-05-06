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

    def test_strips_trailing_punctuation_after_truncation(self):
        result = generate_meta_description(None, "Hello, world and more text", max_chars=10)
        self.assertFalse(result.endswith(","), f"trailing comma not stripped: {result!r}")
        self.assertFalse(result.endswith(" "), f"trailing space not stripped: {result!r}")
        self.assertIn("Hello", result)


from seo_helpers import strip_markdown, detect_language


class TestStripMarkdown(unittest.TestCase):
    def test_removes_headings(self):
        self.assertEqual(strip_markdown("# Title\n\nBody text."), "Title Body text.")

    def test_keeps_link_text_drops_url(self):
        self.assertEqual(
            strip_markdown("See [the docs](https://example.com) for details."),
            "See the docs for details.",
        )

    def test_drops_images_entirely(self):
        self.assertEqual(strip_markdown("Before ![alt](x.png) after"), "Before after")

    def test_strips_bold_italic_code(self):
        self.assertEqual(
            strip_markdown("This is **bold**, *italic*, and `code`."),
            "This is bold, italic, and code.",
        )

    def test_strips_html_tags(self):
        self.assertEqual(strip_markdown("<p>Hello <b>world</b></p>"), "Hello world")


class TestDetectLanguage(unittest.TestCase):
    def test_english_text_returns_en(self):
        self.assertEqual(detect_language("This is an English sentence."), "en")

    def test_chinese_text_returns_zh_tw(self):
        self.assertEqual(detect_language("這是一段中文。"), "zh-TW")

    def test_mixed_majority_chinese_returns_zh_tw(self):
        # >30% CJK chars trips zh-TW
        self.assertEqual(detect_language("Project 計畫名稱 中文佔多數"), "zh-TW")

    def test_empty_input_returns_default_en(self):
        self.assertEqual(detect_language(""), "en")
