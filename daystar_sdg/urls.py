"""
URL configuration for daystar_sdg project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from impact_tracker.views import (
    SDGGoalViewSet, ActivityViewSet, DepartmentViewSet, ResearcherViewSet,
    dashboard_summary, analytics_trends, dashboard_stats, benchmark_comparison
)
from impact_tracker.reports import generate_sdg_report_pdf, generate_comprehensive_report
from django.conf import settings
from django.conf.urls.static import static

# Create API router
router = DefaultRouter()
router.register(r'sdg', SDGGoalViewSet, basename='sdg')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'researchers', ResearcherViewSet, basename='researcher')

urlpatterns = [
    path('admin/', admin.site.urls),

     # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API routes
    path('api/', include(router.urls)),
    
    # New dashboard stats endpoint from roadmap
    path('api/dashboard-stats/', dashboard_stats, name='dashboard-stats'),
path('api/benchmark/', benchmark_comparison, name='benchmark-comparison'),
    
    # Existing report/analytics endpoints
    path('api/reports/summary/', dashboard_summary, name='dashboard-summary'),
    path('api/analytics/trends/', analytics_trends, name='analytics-trends'),
    path('api/reports/generate/<int:sdg_id>/', generate_sdg_report_pdf, name='generate-sdg-report'),
    path('api/reports/comprehensive/', generate_comprehensive_report, name='comprehensive-report'),
    
    # Authentication
    path('api/auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

