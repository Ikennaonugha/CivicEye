from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from .forms import CivicFlagForm
from .models import ProcurementProject, CivicFlag

# List of all 20 official Lagos Local Government Areas
LAGOS_LGAS = [
    'Agege',
    'Ajeromi-Ifelodun',
    'Alimosho',
    'Amuwo-Odofin',
    'Apapa',
    'Badagry',
    'Epe',
    'Eti-Osa',
    'Ibeju-Lekki',
    'Ifako-Ijaiye',
    'Ikeja',
    'Ikorodu',
    'Kosofe',
    'Lagos Island',
    'Lagos Mainland',
    'Mushin',
    'Ojo',
    'Oshodi-Isolo',
    'Shomolu',
    'Surulere',
]


def project_list_view(request):
    selected_lga = request.GET.get('lga', '')
    
    projects_qs = ProcurementProject.objects.all().order_by('-created_at')
    if selected_lga:
        projects_qs = projects_qs.filter(lga=selected_lga)

    paginator = Paginator(projects_qs, 9)
    page_number = request.GET.get('page')
    projects_page = paginator.get_page(page_number)

    context = {
        'projects': projects_page,
        'selected_lga': selected_lga,
        'lagos_lgas': LAGOS_LGAS,
    }
    return render(request, 'flags/project_list.html', context)


def get_client_ip(request):
    """Utility helper to capture the client's real IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def submit_flag(request, project_id):
    project = get_object_or_404(ProcurementProject, pk=project_id)

    if request.method == 'POST':
        form = CivicFlagForm(request.POST, request.FILES)

        # 1. Validate Form & CAPTCHA first (applies to ALL users)
        if form.is_valid():
            user_ip = get_client_ip(request)

            # 2. Total Submissions Limit Check for Unauthenticated / Guest Users
            if not request.user.is_authenticated:
                total_guest_flags = CivicFlag.objects.filter(ip_address=user_ip).count()

                if total_guest_flags >= 2:
                    messages.error(
                        request,
                        "Guest users are limited to 2 total flag reports. Please log in or create an account to file additional flags."
                    )
                    return render(request, 'flags/submit_flag.html', {
                        'form': form,
                        'project': project,
                    })

            # 3. Save Submission
            flag = form.save(commit=False)
            flag.project = project
            flag.ip_address = user_ip

            if request.user.is_authenticated:
                flag.user = request.user

            flag.save()

            messages.success(request, "Your civic flag report has been submitted successfully.")
            return redirect('flags:project_list')
    else:
        form = CivicFlagForm()

    return render(request, 'flags/submit_flag.html', {
        'form': form,
        'project': project,
    })

def project_detail_view(request, project_id):
    """Displays detailed procurement project information and all public civic flags."""
    project = get_object_or_404(ProcurementProject, pk=project_id)
    # Fetch all flags for this project, newest first
    flags = project.flags.all().order_by('-created_at')

    context = {
        'project': project,
        'flags': flags,
    }
    return render(request, 'flags/project_detail.html', context)