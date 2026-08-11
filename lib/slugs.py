import re


def slugify_title(text, max_words=7):
    """Lowercase, hyphenated slug keeping the first `max_words` significant words."""
    words = re.sub(r'[^a-z0-9\s-]', '', text.lower()).split()
    return '-'.join(words[:max_words]).strip('-')
