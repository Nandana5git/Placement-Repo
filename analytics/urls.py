from django.urls import path
from .views import AdminAnalyticsDashboard, ExportReportView

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', AdminAnalyticsDashboard.as_view(), name='dashboard'),
    path('export/', ExportReportView.as_view(), name='export_report'),
]
