from django.contrib import admin

from bookmarks.models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at", "updated_at")
    search_fields = ("user__username", "article__title", "note")
