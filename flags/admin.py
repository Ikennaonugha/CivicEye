# flags/admin.py
from django.contrib import admin
from .models import CivicFlag, ProcurementProject


@admin.register(ProcurementProject)
class ProcurementProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'contract_id', 'state', 'lga', 'status', 'budget')
    list_filter = ('state', 'status')
    search_fields = ('title', 'contract_id', 'contractor', 'lga')


@admin.register(CivicFlag)
class CivicFlagAdmin(admin.ModelAdmin):
    list_display = (
        'project',
        'issue_type',
        'headline',
        'status',
        'created_at',
        'reporter',
    )
    list_filter = ('issue_type', 'status', 'created_at')
    search_fields = ('headline', 'description', 'project__title')
    list_editable = ('status',)