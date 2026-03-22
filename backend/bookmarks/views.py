from rest_framework import permissions, viewsets

from bookmarks.models import Bookmark
from bookmarks.serializers import BookmarkSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Bookmark.objects.filter(user=self.request.user)
            .select_related("article", "article__source")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save()
