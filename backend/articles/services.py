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


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.utils import get_stop_words
from textblob import TextBlob
import nltk

def _ensure_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')

def summarize_article_content(title, source_name, category, content, fallback_text=""):
    text = content or fallback_text
    if not text:
        return "No content available to summarize."

    try:
        _ensure_nltk_data()
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summarizer.stop_words = get_stop_words("english")
        
        summary_sentences = summarizer(parser.document, 4)
        summary = " ".join([str(sentence) for sentence in summary_sentences])
        
        if len(summary) < 20:
            return text[:280] + "..."
            
        return summary
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Summarization failed: %s", e)
        return text[:280] + "..."


def analyze_sentiment(content, fallback_text=""):
    text = content or fallback_text
    if not text:
        return {"score": 0.0, "label": "Neutral"}
        
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    
    if score > 0.1:
        label = "Positive"
    elif score < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
        
    return {"score": score, "label": label}
