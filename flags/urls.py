from django.urls import path
from . import views

app_name = 'flags'

urlpatterns = [
    path('', views.project_list_view, name='project_list'),
    path(
        'project/<int:project_id>/flag/',
        views.submit_flag,
        name='submit_flag',
    ),
    path(
        'project/<int:project_id>/',
        views.project_detail_view,
        name='project_detail',
    ),
]