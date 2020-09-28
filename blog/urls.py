from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.schedule, name='schedule'),
    path('offline', views.offline, name='offline'),
    path('login', views.post_list, name='post_list'),
    path('assignment', views.getAssignment, name="getAssignment"),
    path('assignment-detail', views.getAssignmentDetail, name="getAssignmentDetail"),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='sw.js'),
    path('manifest.json', views.manifest, name='manifest.json')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)