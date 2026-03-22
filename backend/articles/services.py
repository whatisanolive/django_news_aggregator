import re
from html import unescape
from html.parser import HTMLParser

import requests
from django.conf import settings


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._ignore_depth = 0
        self._chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self._ignore_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self._ignore_depth:
            self._ignore_depth -= 1
        if tag in {"p", "div", "article", "section", "br", "li", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_data(self, data):
        if self._ignore_depth:
            return
        text = data.strip()
        if text:
            self._chunks.append(text)

    @property
    def text(self):
        raw = " ".join(self._chunks)
        raw = re.sub(r"\s*\n\s*", "\n", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        raw = re.sub(r"[ \t]{2,}", " ", raw)
        return raw.strip()


def _extract_meta_image(html):
    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if match:
            return unescape(match.group(1))
    return ""


def _extract_paragraph_content(html):
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html, flags=re.IGNORECASE | re.DOTALL)
    cleaned = []
    for paragraph in paragraphs:
        without_tags = re.sub(r"<[^>]+>", " ", paragraph)
        without_tags = unescape(without_tags)
        without_tags = re.sub(r"\s+", " ", without_tags).strip()
        if len(without_tags) > 40:
            cleaned.append(without_tags)
    return "\n\n".join(cleaned)


def scrape_article_content(url, fallback_text=""):
    response = requests.get(
        url,
        timeout=settings.ARTICLE_FETCH_TIMEOUT,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    html = response.text
    paragraph_text = _extract_paragraph_content(html)

    if not paragraph_text:
        parser = _TextExtractor()
        parser.feed(html)
        paragraph_text = parser.text

    content = paragraph_text or fallback_text
    content = re.sub(r"\n{3,}", "\n\n", content).strip()

    return {
        "content": content[: settings.ARTICLE_SUMMARY_MAX_CHARS],
        "image_url": _extract_meta_image(html),
    }


def summarize_article_content(title, source_name, category, content, fallback_text=""):
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        text = fallback_text or content
        return text[:280] if text else "Summary unavailable until GEMINI_API_KEY is configured."

    prompt = (
        "You are summarizing a news article for a niche aggregator focused on business "
        "and technology. Write a concise 3-4 sentence summary in plain English. "
        "Avoid hype, avoid bullet points, mention the key development and why it matters.\n\n"
        f"Category: {category}\n"
        f"Source: {source_name}\n"
        f"Title: {title}\n\n"
        f"Article:\n{content[: settings.ARTICLE_SUMMARY_MAX_CHARS]}"
    )

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent",
        params={"key": api_key},
        timeout=settings.ARTICLE_FETCH_TIMEOUT,
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ]
        },
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini returned no summary candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    summary = "\n".join(part.get("text", "").strip() for part in parts if part.get("text")).strip()
    if not summary:
        raise ValueError("Gemini response did not include summary text.")
    return summary
