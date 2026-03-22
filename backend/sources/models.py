from django.db import models

class Source(models.Model):
    class Category(models.TextChoices):
        BUSINESS = "business", "Business"
        TECH = "tech", "Tech"

    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200)
    rss_url = models.URLField(unique=True)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.BUSINESS,
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.category})"
