from rest_framework.routers import DefaultRouter

from bookmarks.views import BookmarkViewSet

router = DefaultRouter()
router.register("", BookmarkViewSet, basename="bookmark")

urlpatterns = router.urls
