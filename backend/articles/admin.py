from django.contrib import admin

from articles.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "category", "published_at", "summary_status")
    list_filter = ("category", "summary_status", "source")
    search_fields = ("title", "url", "summary", "rss_excerpt")
