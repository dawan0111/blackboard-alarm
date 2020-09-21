from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.schedule, name='schedule'),
    path('login', views.post_list, name='post_list'),
    path('assignment', views.getAssignment, name="getAssignment"),
    path('assignment-detail', views.getAssignmentDetail, name="getAssignmentDetail")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)