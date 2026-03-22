from rest_framework import serializers

from articles.models import Article
from bookmarks.models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        source="article",
        write_only=True,
    )
    article = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bookmark
        fields = [
            "id",
            "article_id",
            "article",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_article(self, obj):
        return {
            "id": obj.article_id,
            "title": obj.article.title,
            "url": obj.article.url,
            "summary": obj.article.summary,
            "category": obj.article.category,
            "source_name": obj.article.source.name,
        }

    def create(self, validated_data):
        user = self.context["request"].user
        bookmark, _ = Bookmark.objects.update_or_create(
            user=user,
            article=validated_data["article"],
            defaults={"note": validated_data.get("note", "")},
        )
        return bookmark
