from django.conf import settings
from django.db import models


class ProcurementProject(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing Work'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned / Stalled'),
        ('planned', 'Planned'),
    ]

    title = models.CharField(max_length=255)
    contract_id = models.CharField(
        max_length=100, unique=True, help_text='OCDS or Government Ref ID'
    )
    description = models.TextField()
    procuring_entity = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Ministry, Department, or Agency (e.g., Ministry of Works)',
    )
    contractor = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=15, decimal_places=2)

    # Geographic Metadata
    state = models.CharField(max_length=100, default='Lagos', db_index=True)
    lga = models.CharField(
        max_length=100, db_index=True, verbose_name='LGA'
    )
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ongoing'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} ({self.lga}, {self.state})'


class CivicFlag(models.Model):
    FLAG_TYPES = [
        ('ghost', 'Ghost Project (No work on ground)'),
        ('delay', 'Unexplained Delay / Inactive Site'),
        ('quality', 'Substandard Materials / Poor Quality'),
        ('misappropriation', 'Suspected Misappropriation'),
        ('other', 'Other Issue'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Investigation'),
        ('verified', 'Verified Flag'),
        ('dismissed', 'Dismissed'),
    ]

    project = models.ForeignKey(
        ProcurementProject, on_delete=models.CASCADE, related_name='flags'
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_flags',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flags',
    )

    issue_type = models.CharField(max_length=50, choices=FLAG_TYPES)
    headline = models.CharField(max_length=200)
    description = models.TextField()

    # Evidence Uploads & On-Site Verification
    evidence_image = models.ImageField(
        upload_to='civic_flags/evidence/', null=True, blank=True
    )
    user_latitude = models.FloatField(
        null=True, blank=True
    )  # Captured automatically via browser GPS
    user_longitude = models.FloatField(null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_issue_type_display()}] Flag on {self.project.title}"