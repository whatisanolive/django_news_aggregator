from rest_framework import generics

from articles.models import Article
from articles.serializers import ArticleDetailSerializer, ArticleListSerializer


class ArticleListAPIView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    filterset_fields = ["category", "source"]
    search_fields = ["title", "summary", "rss_excerpt", "source__name"]
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at", "-created_at"]

    def get_queryset(self):
        queryset = Article.objects.select_related("source")
        summary_ready = self.request.query_params.get("summary_ready")
        if summary_ready == "true":
            queryset = queryset.exclude(summary="")
        return queryset


class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.select_related("source")
    serializer_class = ArticleDetailSerializer
