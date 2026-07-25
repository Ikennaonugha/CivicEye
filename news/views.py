from django.db.models import Count, OuterRef, Q, Subquery
from django.shortcuts import render
from .models import GovernmentNewsArticle


def gov_news_feed(request):
    selected_category = request.GET.get('category', 'all')
    query = request.GET.get('q', '').strip()

    # 1. Subquery: Count how many times each image_url appears across the DB
    image_usage_subquery = (
        GovernmentNewsArticle.objects.filter(image_url=OuterRef('image_url'))
        .exclude(Q(image_url__isnull=True) | Q(image_url=''))
        .values('image_url')
        .annotate(cnt=Count('id'))
        .values('cnt')
    )

    # 2. Base QuerySet: Only articles with valid image URLs
    articles = GovernmentNewsArticle.objects.exclude(
        Q(image_url__isnull=True) | Q(image_url='')
    )

    # 3. Exclude repeated channel/site logos (images appearing 3+ times)
    articles = (
        articles.annotate(img_usage_count=Subquery(image_usage_subquery))
        .filter(
            img_usage_count__lte=2
        )  # Keeps unique article pictures (used 1-2 times max)
        .order_by('-published_date')
    )

    # 4. Filter by Category
    if selected_category and selected_category != 'all':
        articles = articles.filter(category=selected_category)

    # 5. Filter by Search Term
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(summary__icontains=query)
        )

    # Category choices array for UI pills
    categories = [
        ('gov', 'Governance'),
        ('economy', 'Economy & Business'),
        ('tech', 'Tech & Innovation'),
        ('society', 'Society'),
    ]

    context = {
        'news_articles': articles,
        'selected_category': selected_category,
        'query': query,
        'categories': categories,
    }

    return render(request, 'news/feed.html', context)