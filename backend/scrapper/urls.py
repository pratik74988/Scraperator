from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse

from . import views

# API Router
router = DefaultRouter()
router.register(r'jobs', views.ScrapeJobViewSet, basename='scrapejob')

app_name = 'scrapper'


def test_view(request):
    return HttpResponse("Test route is working")

urlpatterns = [
    path('api/', include(router.urls)),

    # Template views
    path('test/', test_view, name='test_route'),
    path('', views.dashboard_view, name='dashboard'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('create/', views.create_job_view, name='create_job'),
    path('ai-test/', views.ai_test_view, name='ai_test'),
]


app_name = 'scrapper'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Template views
    path('', views.dashboard_view, name='dashboard'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('create/', views.create_job_view, name='create_job'),
    path('ai-test/', views.ai_test_view, name='ai_test'),
]