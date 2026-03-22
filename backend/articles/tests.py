from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article
from bookmarks.models import Bookmark
from sources.models import Source


class ApiFlowTests(APITestCase):
    def setUp(self):
        self.source = Source.objects.create(
            name="Tech Source",
            domain="example.com",
            rss_url="https://example.com/feed.xml",
            category=Source.Category.TECH,
        )
        self.article = Article.objects.create(
            title="AI startup raises funding",
            url="https://example.com/article",
            rss_excerpt="A short RSS summary.",
            content="A full scraped article body.",
            summary="A concise summary.",
            source=self.source,
            category=Source.Category.TECH,
            published_at=timezone.now() - timedelta(hours=1),
            summary_status=Article.SummaryStatus.COMPLETED,
        )
        self.user = User.objects.create_user(
            username="demo",
            email="demo@example.com",
            password="strongpass123",
        )

    def test_public_article_listing(self):
        response = self.client.get(reverse("article-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], self.article.title)

    def test_register_login_and_bookmark(self):
        register_response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "anotherpass123",
            },
            format="json",
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "username": "demo",
                "password": "strongpass123",
            },
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )
        bookmark_response = self.client.post(
            reverse("bookmark-list"),
            {
                "article_id": self.article.id,
                "note": "Read this before Monday meeting.",
            },
            format="json",
        )
        self.assertEqual(bookmark_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bookmark.objects.count(), 1)
