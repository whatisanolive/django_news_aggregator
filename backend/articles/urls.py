from django.urls import path, include
from rest_framework.routers import DefaultRouter

from articles.views import ArticleDetailAPIView, ArticleListAPIView, ArticleVoteAPIView, CommentViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path("", ArticleListAPIView.as_view(), name="article-list"),
    path("<int:pk>/", ArticleDetailAPIView.as_view(), name="article-detail"),
    path("<int:pk>/vote/", ArticleVoteAPIView.as_view(), name="article-vote"),
    path("", include(router.urls)),
]
