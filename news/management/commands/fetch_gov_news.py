from datetime import datetime
import re
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
import feedparser
import requests
from news.models import GovernmentNewsArticle

FEED_CONFIG = [
    # Governance & Politics
    {
        'category': 'gov',
        'source': 'Premium Times',
        'url': 'https://www.premiumtimesng.com/category/news/top-news/feed',
    },
    {
        'category': 'gov',
        'source': 'Punch',
        'url': 'https://punchng.com/topics/news/feed/',
    },
    # Economy & Business
    {
        'category': 'economy',
        'source': 'BusinessDay',
        'url': 'https://businessday.ng/feed/',
    },
    {
        'category': 'economy',
        'source': 'Nairametrics',
        'url': 'https://nairametrics.com/feed/',
    },
    # Tech & Innovation
    {
        'category': 'tech',
        'source': 'TechCabal',
        'url': 'https://techcabal.com/feed/',
    },
    {
        'category': 'tech',
        'source': 'Techpoint Africa',
        'url': 'https://techpoint.africa/feed/',
    },
    # Society & Education
    {
        'category': 'society',
        'source': 'Vanguard',
        'url': 'https://www.vanguardngr.com/category/national-news/feed/',
    },
]

# Browser User-Agent to bypass CDN/Cloudflare SSL blocks
HTTP_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    ),
}


def extract_image_url(entry):
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        return entry.media_thumbnail[0].get('url')
    if hasattr(entry, 'media_content') and entry.media_content:
        return entry.media_content[0].get('url')

    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/') or any(
                enc.get('href', '').lower().endswith(ext)
                for ext in ['.jpg', '.jpeg', '.png', '.webp']
            ):
                return enc.get('href')

    html_sources = []
    if hasattr(entry, 'content') and entry.content:
        for c in entry.content:
            html_sources.append(c.get('value', ''))
    html_sources.append(getattr(entry, 'summary', ''))
    html_sources.append(getattr(entry, 'description', ''))

    full_html = ' '.join(html_sources)

    candidate_urls = re.findall(
        r'(?:src|data-src|data-lazy-src|srcset)=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)["\']',
        full_html,
        re.IGNORECASE,
    )

    if not candidate_urls:
        candidate_urls = re.findall(
            r'(https?://[^\s"\'>]+\.(?:jpg|jpeg|png|webp))',
            full_html,
            re.IGNORECASE,
        )

    for url in candidate_urls:
        clean_url = url.split(',')[0].split(' ')[0]
        if (
            'data:image' not in clean_url
            and '1x1' not in clean_url
            and 'avatar' not in clean_url
        ):
            return clean_url

    return None


class Command(BaseCommand):
    help = 'Fetches categorized news feeds safely across Governance, Tech, Business, and Society.'

    def handle(self, *args, **options):
        saved_count = 0

        for feed_info in FEED_CONFIG:
            source = feed_info['source']
            url = feed_info['url']
            category = feed_info['category']

            self.stdout.write(f'Scanning [{category.upper()}] feed: {source}...')

            # Safely fetch content with requests before passing to feedparser
            try:
                response = requests.get(
                    url, headers=HTTP_HEADERS, timeout=12, verify=True
                )
                response.raise_for_status()
                feed = feedparser.parse(response.content)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'   └── Skipping {source} due to connection error: {e}'
                    )
                )
                continue

            for entry in feed.entries:
                title = getattr(entry, 'title', '').strip()
                if not title:
                    continue

                summary = getattr(entry, 'summary', '') or getattr(
                    entry, 'description', ''
                )
                link = getattr(entry, 'link', '')
                if not link:
                    continue

                image_url = extract_image_url(entry)

                parsed_date = None
                if (
                    hasattr(entry, 'published_parsed')
                    and entry.published_parsed
                ):
                    naive_dt = datetime.fromtimestamp(
                        time.mktime(entry.published_parsed)
                    )
                    parsed_date = timezone.make_aware(naive_dt)

                article, created = GovernmentNewsArticle.objects.get_or_create(
                    link=link,
                    defaults={
                        'title': title,
                        'source': source,
                        'summary': summary,
                        'image_url': image_url,
                        'published_date': parsed_date,
                        'category': category,
                    },
                )

                if not created and image_url and article.image_url != image_url:
                    article.image_url = image_url
                    article.save()

                if created:
                    saved_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Sync complete. Ingested {saved_count} new categorized articles.'
            )
        )