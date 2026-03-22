from django.core.management.base import BaseCommand

from sources.models import Source


DEFAULT_SOURCES = [
    {
        "name": "Reuters Business",
        "domain": "reuters.com",
        "rss_url": "https://feeds.reuters.com/reuters/businessNews",
        "category": Source.Category.BUSINESS,
        "description": "Global business reporting from Reuters.",
    },
    {
        "name": "CNBC Business",
        "domain": "cnbc.com",
        "rss_url": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
        "category": Source.Category.BUSINESS,
        "description": "Market and company coverage from CNBC.",
    },
    {
        "name": "TechCrunch",
        "domain": "techcrunch.com",
        "rss_url": "https://techcrunch.com/feed/",
        "category": Source.Category.TECH,
        "description": "Startup and technology reporting from TechCrunch.",
    },
    {
        "name": "The Verge Tech",
        "domain": "theverge.com",
        "rss_url": "https://www.theverge.com/rss/tech/index.xml",
        "category": Source.Category.TECH,
        "description": "Consumer and platform technology coverage from The Verge.",
    },
]


class Command(BaseCommand):
    help = "Seed the project with two business and two tech RSS sources."

    def handle(self, *args, **options):
        for source_data in DEFAULT_SOURCES:
            source, created = Source.objects.update_or_create(
                rss_url=source_data["rss_url"],
                defaults={**source_data, "is_active": True},
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} {source.name}"))
