from django.contrib import admin

from sources.models import Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "domain", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "domain", "rss_url")
