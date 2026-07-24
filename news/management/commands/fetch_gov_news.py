from datetime import datetime
import re
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
import feedparser
from news.models import GovernmentNewsArticle

FEEDS = [
    (
        'Premium Times - Politics & Gov',
        'https://www.premiumtimesng.com/category/news/top-news/feed',
    ),
    ('Punch - Politics', 'https://punchng.com/topics/news/politics/feed/'),
    ('Vanguard - National', 'https://www.vanguardngr.com/category/national-news/feed/'),
    ('Channels TV - Politics', 'https://www.channelstv.com/category/politics/feed/'),
    ('The Guardian - Governance', 'https://guardian.ng/category/news/nigeria/national/feed/'),
]

GOV_KEYWORDS = [
    'government',
    'federal',
    'ministry',
    'minister',
    'procurement',
    'budget',
    'senate',
    'house of reps',
    'national assembly',
    'presidency',
    'cbn',
    'efcc',
    'icpc',
    'policy',
    'governor',
    'gazette',
    'allocation',
    'statutory',
    'tenders',
    'contract',
    'audit',
]


def extract_image_url(entry):
    """Extracts image URLs from media tags, enclosures, or HTML content,

    handling WordPress lazy loading (data-src) and CDN host restrictions.
    """
    # 1. Media content / thumbnail tags
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        return entry.media_thumbnail[0].get('url')
    if hasattr(entry, 'media_content') and entry.media_content:
        return entry.media_content[0].get('url')

    # 2. File enclosures
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/') or any(
                enc.get('href', '').lower().endswith(ext)
                for ext in ['.jpg', '.jpeg', '.png', '.webp']
            ):
                return enc.get('href')

    # 3. Gather all HTML sources
    html_sources = []
    if hasattr(entry, 'content') and entry.content:
        for c in entry.content:
            html_sources.append(c.get('value', ''))
    html_sources.append(getattr(entry, 'summary', ''))
    html_sources.append(getattr(entry, 'description', ''))

    full_html = ' '.join(html_sources)

    # 4. Search for lazy-loaded image attributes (data-src, data-lazy-src, src)
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
    help = 'Fetches Nigerian news feeds and filters specifically for government & civic topics with images.'

    def handle(self, *args, **options):
        saved_count = 0

        for source_name, url in FEEDS:
            self.stdout.write(f'Scanning feed: {source_name}...')
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = entry.title
                summary = getattr(entry, 'summary', '') or getattr(
                    entry, 'description', ''
                )
                combined_text = f'{title} {summary}'.lower()

                if any(keyword in combined_text for keyword in GOV_KEYWORDS):
                    link = entry.link
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
                            'source': source_name,
                            'summary': summary,
                            'image_url': image_url,
                            'published_date': parsed_date,
                        },
                    )

                    # Update existing record if image URL was previously missing or updated
                    if (
                        not created
                        and image_url
                        and article.image_url != image_url
                    ):
                        article.image_url = image_url
                        article.save()

                    if created:
                        saved_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Sync complete. Ingested {saved_count} government news articles.'
            )
        )