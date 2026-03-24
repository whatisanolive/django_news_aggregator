import datetime
import logging

import feedparser
from celery import shared_task
from django.utils import timezone

from articles.models import Article
from articles.services import scrape_article_content, summarize_article_content, analyze_sentiment
from sources.models import Source

logger = logging.getLogger(__name__)


def _parse_published_datetime(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        naive = datetime.datetime(*entry.published_parsed[:6])
        return timezone.make_aware(naive, datetime.timezone.utc)
    return None


@shared_task
def fetch_rss_articles(source_id=None):
    sources = Source.objects.filter(is_active=True)
    if source_id is not None:
        sources = sources.filter(id=source_id)

    for source in sources:
        feed = feedparser.parse(
            source.rss_url,
            request_headers={
                "User-Agent": "Mozilla/5.0",
            },
        )

        for entry in feed.entries:
            url = entry.get("link")
            if not url:
                continue

            article, created = Article.objects.get_or_create(
                url=url,
                defaults={
                    "title": entry.get("title", "Untitled article"),
                    "rss_excerpt": entry.get("summary", ""),
                    "source": source,
                    "category": source.category,
                    "image_url": (
                        entry.get("media_content", [{}])[0].get("url", "")
                        if entry.get("media_content")
                        else ""
                    ),
                    "author": entry.get("author", ""),
                    "published_at": _parse_published_datetime(entry),
                },
            )

            if not created:
                article.title = entry.get("title", article.title)
                article.rss_excerpt = entry.get("summary", article.rss_excerpt)
                article.author = entry.get("author", article.author)
                article.category = source.category
                if not article.published_at:
                    article.published_at = _parse_published_datetime(entry)
                article.save(
                    update_fields=[
                        "title",
                        "rss_excerpt",
                        "author",
                        "category",
                        "published_at",
                        "updated_at",
                    ]
                )

            scrape_and_summarize_article.delay(article.id)


@shared_task
def scrape_and_summarize_article(article_id):
    article = Article.objects.select_related("source").get(id=article_id)
    result = scrape_article_content(article.url, fallback_text=article.rss_excerpt)

    article.content = result["content"]
    article.scraped_at = timezone.now()

    if result["image_url"] and not article.image_url:
        article.image_url = result["image_url"]

    if not article.content:
        article.summary_status = Article.SummaryStatus.FAILED
        article.summary_error = "No article body could be extracted from the source page."
        article.save(
            update_fields=[
                "content",
                "scraped_at",
                "image_url",
                "summary_status",
                "summary_error",
                "updated_at",
            ]
        )
        return

    try:
        summary = summarize_article_content(
            title=article.title,
            source_name=article.source.name,
            category=article.category,
            content=article.content,
            fallback_text=article.rss_excerpt,
        )
        sentiment_data = analyze_sentiment(
            content=article.content,
            fallback_text=article.rss_excerpt,
        )
        article.summary = summary
        article.sentiment_score = sentiment_data["score"]
        article.sentiment_label = sentiment_data["label"]
        article.summary_status = Article.SummaryStatus.COMPLETED
        article.summary_error = ""
        article.summarized_at = timezone.now()
    except Exception as exc:
        logger.exception("Failed to summarize or analyze sentiment for article %s", article.id)
        article.summary = article.rss_excerpt[:500]
        article.summary_status = Article.SummaryStatus.FAILED
        article.summary_error = str(exc)

    article.save(
        update_fields=[
            "content",
            "summary",
            "sentiment_score",
            "sentiment_label",
            "summary_status",
            "summary_error",
            "scraped_at",
            "summarized_at",
            "image_url",
            "updated_at",
        ]
    )
