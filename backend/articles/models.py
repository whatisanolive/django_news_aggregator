from django.db import models
from sources.models import Source

class Article(models.Model):
    class SummaryStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    rss_excerpt = models.TextField(blank=True)
    content = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=20, blank=True)
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    category = models.CharField(
        max_length=20,
        choices=Source.Category.choices,
        default=Source.Category.BUSINESS,
    )
    image_url = models.URLField(blank=True)
    author = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    summary_status = models.CharField(
        max_length=20,
        choices=SummaryStatus.choices,
        default=SummaryStatus.PENDING,
    )
    summary_error = models.TextField(blank=True)
    scraped_at = models.DateTimeField(null=True, blank=True)
    summarized_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.source_id:
            self.category = self.source.category
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
        models.Index(fields=["published_at"]),
        models.Index(fields=["summary_status"]),
        ]
        

    def __str__(self):
        return self.title
