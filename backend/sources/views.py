from django.db.models import Count
from rest_framework import generics

from sources.models import Source
from sources.serializers import SourceSerializer


class SourceListAPIView(generics.ListAPIView):
    serializer_class = SourceSerializer
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "domain", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["category", "name"]

    def get_queryset(self):
        return Source.objects.filter(is_active=True).annotate(article_count=Count("articles"))
