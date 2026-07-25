from django.db import models


class GovernmentNewsArticle(models.Model):
    CATEGORY_CHOICES = [
        ('gov', 'Governance & Policy'),
        ('economy', 'Economy & Business'),
        ('tech', 'Tech & Innovation'),
        ('society', 'Society & Education'),
        ('general', 'General News'),
    ]

    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    source = models.CharField(max_length=100)
    summary = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, max_length=1000)
    published_date = models.DateTimeField(null=True, blank=True)

    # New Category Field
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='gov', db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[{self.get_category_display()}] {self.title}'