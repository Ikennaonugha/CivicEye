# news/models.py
from django.db import models


class GovernmentNewsArticle(models.Model):
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    source = models.CharField(max_length=100)
    summary = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True)  # New field
    published_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = 'Government News Article'

    def __str__(self):
        return f'[{self.source}] {self.title}'