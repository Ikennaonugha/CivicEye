from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CivicFlagForm
from .models import ProcurementProject

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
    """Lists ongoing procurement projects defaulting exclusively to Lagos State."""
    selected_state = request.GET.get('state', 'Lagos').strip()
    selected_lga = request.GET.get('lga', '').strip()

    projects = ProcurementProject.objects.annotate(
        total_flags=Count('flags')
    ).order_by('-created_at')

    if selected_state:
        projects = projects.filter(state__iexact=selected_state)

    if selected_lga:
        projects = projects.filter(lga__iexact=selected_lga)

    context = {
        'projects': projects,
        'selected_state': selected_state,
        'selected_lga': selected_lga,
        'lagos_lgas': LAGOS_LGAS,
    }
    return render(request, 'flags/project_list.html', context)


def submit_flag_view(request, project_id):
    """Handles submission of civic flags/reports for a specific project."""
    project = get_object_or_404(ProcurementProject, pk=project_id)

    if request.method == 'POST':
        form = CivicFlagForm(request.POST, request.FILES)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.project = project
            if request.user.is_authenticated:
                flag.user = request.user
            flag.save()
            messages.success(
                request,
                'Your report has been submitted and flagged for audit.',
            )
            return redirect('flags:project_list')
    else:
        form = CivicFlagForm()

    context = {
        'project': project,
        'form': form,
    }
    return render(request, 'flags/submit_flag.html', context)

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