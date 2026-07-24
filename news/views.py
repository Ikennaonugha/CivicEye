# news/views.py
from django.db.models import (
    Case,
    Count,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.shortcuts import render
from .models import GovernmentNewsArticle


def gov_news_feed(request):
    query = request.GET.get('q', '').strip()

    articles = GovernmentNewsArticle.objects.all()

    # Filter by keyword if search input is used
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(summary__icontains=query)
        )

    # Subquery: Count articles sharing the exact same image_url
    image_count_subquery = (
        GovernmentNewsArticle.objects.filter(image_url=OuterRef('image_url'))
        .exclude(Q(image_url__isnull=True) | Q(image_url=''))
        .values('image_url')
        .annotate(count=Count('id'))
        .values('count')
    )

    # Priority ranking (Tier 1: Unique Image, Tier 2: Shared Logo, Tier 3: No Image)
    articles = (
        articles.annotate(
            img_count=Subquery(
                image_count_subquery, output_field=IntegerField()
            )
        )
        .annotate(
            image_priority=Case(
                When(
                    Q(image_url__isnull=False)
                    & ~Q(image_url='')
                    & Q(img_count=1),
                    then=Value(1),
                ),
                When(
                    Q(image_url__isnull=False)
                    & ~Q(image_url='')
                    & Q(img_count__gt=1),
                    then=Value(2),
                ),
                default=Value(3),
                output_field=IntegerField(),
            )
        )
        .order_by('image_priority', '-published_date')
    )

    context = {
        'news_articles': articles,
        'query': query,
    }

    return render(request, 'news/feed.html', context)