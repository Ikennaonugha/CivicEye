from django.shortcuts import render
from django.db.models import Sum, Count
from procurement.models import ContractingRelease

def dashboard_home(request):
    # 1. KPI Summary Cards
    total_volume = ContractingRelease.objects.aggregate(
        total=Sum('budget_amount')
    )['total'] or 0

    total_processes = ContractingRelease.objects.values('ocid').distinct().count()
    total_buyers = ContractingRelease.objects.values('buyer_name').distinct().count()
    total_releases = ContractingRelease.objects.count()

    # 2. Top 5 Buyers by Spending (for Bar Chart)
    top_buyers_qs = (
        ContractingRelease.objects
        .exclude(buyer_name__isnull=True)
        .values('buyer_name')
        .annotate(total_spend=Sum('budget_amount'))
        .order_by('-total_spend')[:5]
    )
    buyer_labels = [b['buyer_name'] for b in top_buyers_qs]
    buyer_data = [float(b['total_spend'] or 0) for b in top_buyers_qs]

    # 3. Tender Status Distribution (for Donut Chart)
    status_qs = (
        ContractingRelease.objects
        .exclude(tender_status__isnull=True)
        .values('tender_status')
        .annotate(count=Count('id'))
    )
    status_labels = [s['tender_status'].title() for s in status_qs]
    status_data = [s['count'] for s in status_qs]

    # 4. Recent Releases (for Data Table)
    recent_releases = ContractingRelease.objects.order_by('-date')[:10]

    context = {
        'total_volume': total_volume,
        'total_processes': total_processes,
        'total_buyers': total_buyers,
        'total_releases': total_releases,
        'buyer_labels': buyer_labels,
        'buyer_data': buyer_data,
        'status_labels': status_labels,
        'status_data': status_data,
        'recent_releases': recent_releases,
    }

    return render(request, 'dashboard.html', context)