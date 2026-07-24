from django.shortcuts import render
from django.db.models import Sum, Count, Q
from procurement.models import ContractingRelease as Release


def dashboard_home(request):
    # 1. Capture GET search parameters
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    # Checkbox state handling (default to checked if page first loads)
    has_searched = 'q' in request.GET or 'status' in request.GET
    search_title = request.GET.get('scope_title') == 'on' or not has_searched
    search_buyer = request.GET.get('scope_buyer') == 'on' or not has_searched
    search_ocid = request.GET.get('scope_ocid') == 'on' or not has_searched

    # 2. Base Queryset across ENTIRE Database
    releases_qs = Release.objects.all()

    # Apply database-level keyword filtering
    if q:
        q_filter = Q()
        if not search_title and not search_buyer and not search_ocid:
            # Fallback to searching all fields if no checkboxes are ticked
            q_filter |= Q(tender_title__icontains=q)
            q_filter |= Q(buyer_name__icontains=q)
            q_filter |= Q(ocid__icontains=q) | Q(release_id__icontains=q)
        else:
            if search_title:
                q_filter |= Q(tender_title__icontains=q)
            if search_buyer:
                q_filter |= Q(buyer_name__icontains=q)
            if search_ocid:
                q_filter |= Q(ocid__icontains=q) | Q(release_id__icontains=q)

        releases_qs = releases_qs.filter(q_filter)

    # Apply status filter
    if status:
        releases_qs = releases_qs.filter(tender_status__iexact=status)

    # Fetch top 50 matching releases from database
    matching_count = releases_qs.count()
    recent_releases = releases_qs.order_by('-date')[:50]

    # 3. Overall Dashboard KPIs
    total_volume = (
        Release.objects.aggregate(Sum('budget_amount'))['budget_amount__sum'] or 0
    )
    total_processes = Release.objects.values('ocid').distinct().count()
    total_buyers = Release.objects.values('buyer_name').distinct().count()
    total_releases = Release.objects.count()

    # Top 5 Buyers Chart Data
    buyers_qs = (
        Release.objects.values('buyer_name')
        .annotate(total=Sum('budget_amount'))
        .order_by('-total')[:5]
    )
    buyer_labels = [b['buyer_name'] or 'Unknown Buyer' for b in buyers_qs]
    buyer_data = [float(b['total'] or 0) for b in buyers_qs]

    # Status Breakdown Chart Data
    status_qs = Release.objects.values('tender_status').annotate(
        count=Count('id')
    )
    status_labels = [
        s['tender_status'].capitalize() if s['tender_status'] else 'Unknown'
        for s in status_qs
    ]
    status_data = [s['count'] for s in status_qs]

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
        # Search state variables
        'query': q,
        'selected_status': status,
        'search_title': search_title,
        'search_buyer': search_buyer,
        'search_ocid': search_ocid,
        'matching_count': matching_count if has_searched else None,
    }

    return render(request, 'dashboard.html', context)