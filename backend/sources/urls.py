from django.urls import path

from sources.views import SourceListAPIView

urlpatterns = [
    path("", SourceListAPIView.as_view(), name="source-list"),
]
