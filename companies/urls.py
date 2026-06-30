from django.urls import path
from .views import CompanyDashboardView, CompanyProfileUpdateView

app_name = 'companies'

urlpatterns = [
    path('dashboard/', CompanyDashboardView.as_view(), name='dashboard'),
    path('profile/edit/', CompanyProfileUpdateView.as_view(), name='profile_edit'),
]
