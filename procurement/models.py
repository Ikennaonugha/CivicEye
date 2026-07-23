from django.db import models

class ContractingRelease(models.Model):
    # Open Contracting ID (indexed, but unique per release_id)
    ocid = models.CharField(max_length=255, db_index=True)
    release_id = models.CharField(max_length=50)
    date = models.DateTimeField(null=True, blank=True)
    initiation_type = models.CharField(max_length=100, null=True, blank=True)
    
    # Buyer Details
    buyer_id = models.CharField(max_length=255, null=True, blank=True)
    buyer_name = models.CharField(max_length=500, null=True, blank=True, db_index=True)
    
    # Budget Details (extracted from planning.budget)
    budget_project = models.TextField(null=True, blank=True)
    budget_amount = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    budget_currency = models.CharField(max_length=10, default='NGN')
    
    # Tender Details (extracted if available)
    tender_title = models.TextField(null=True, blank=True)
    tender_value_amount = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    tender_status = models.CharField(max_length=50, null=True, blank=True)
    
    # Store full/nested arrays safely as JSONFields
    tags = models.JSONField(default=list)
    parties = models.JSONField(default=list)
    planning_data = models.JSONField(default=dict, null=True, blank=True)
    tender_data = models.JSONField(default=dict, null=True, blank=True)
    awards_data = models.JSONField(default=list, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ocid', 'release_id'],
                name='unique_ocid_release'
            )
        ]

    def __str__(self):
        return f"{self.ocid} - {self.release_id} - {self.buyer_name}"