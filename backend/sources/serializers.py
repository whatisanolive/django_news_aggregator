from rest_framework import serializers

from sources.models import Source


class SourceSerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Source
        fields = [
            "id",
            "name",
            "domain",
            "rss_url",
            "category",
            "description",
            "is_active",
            "article_count",
        ]
