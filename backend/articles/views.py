from rest_framework import generics, viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from articles.models import Article, Comment, Vote
from articles.serializers import ArticleDetailSerializer, ArticleListSerializer, CommentSerializer


class ArticleListAPIView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    filterset_fields = ["category", "source"]
    search_fields = ["title", "summary", "rss_excerpt", "source__name"]
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at", "-created_at"]

    def get_queryset(self):
        queryset = Article.objects.select_related("source").annotate(
            vote_score=Coalesce(Sum('votes__value'), 0)
        )
        summary_ready = self.request.query_params.get("summary_ready")
        if summary_ready == "true":
            queryset = queryset.exclude(summary="")
        return queryset


class ArticleDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ArticleDetailSerializer

    def get_queryset(self):
        return Article.objects.select_related("source").annotate(
            vote_score=Coalesce(Sum('votes__value'), 0)
        )

class ArticleVoteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        value = request.data.get("value", 0)
        if value not in [1, -1, 0]:
            return Response({"error": "Invalid vote value"}, status=status.HTTP_400_BAD_REQUEST)
        
        content_type = ContentType.objects.get_for_model(Article)
        
        if value == 0:
            Vote.objects.filter(user=request.user, content_type=content_type, object_id=article.id).delete()
        else:
            Vote.objects.update_or_create(
                user=request.user, content_type=content_type, object_id=article.id,
                defaults={"value": value}
            )
        return Response({"status": "voted"})

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.annotate(vote_score=Coalesce(Sum('votes__value'), 0))
        article_id = self.request.query_params.get('article')
        if article_id:
            queryset = queryset.filter(article_id=article_id, parent__isnull=True)
        return queryset.order_by('-vote_score', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        comment = self.get_object()
        value = request.data.get("value", 0)
        if value not in [1, -1, 0]:
            return Response({"error": "Invalid vote value"}, status=status.HTTP_400_BAD_REQUEST)
        
        content_type = ContentType.objects.get_for_model(Comment)
        if value == 0:
            Vote.objects.filter(user=request.user, content_type=content_type, object_id=comment.id).delete()
        else:
            Vote.objects.update_or_create(
                user=request.user, content_type=content_type, object_id=comment.id,
                defaults={"value": value}
            )
        return Response({"status": "voted"})
