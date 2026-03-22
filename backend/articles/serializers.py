from rest_framework import serializers

from articles.models import Article


class ArticleListSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "url",
            "rss_excerpt",
            "summary",
            "source_name",
            "category",
            "image_url",
            "author",
            "published_at",
            "summary_status",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "url",
            "rss_excerpt",
            "content",
            "summary",
            "source",
            "category",
            "image_url",
            "author",
            "published_at",
            "summary_status",
            "summary_error",
            "created_at",
            "updated_at",
        ]

    def get_source(self, obj):
        return {
            "id": obj.source_id,
            "name": obj.source.name,
            "domain": obj.source.domain,
            "category": obj.source.category,
        }
