from django.urls import path
from .views import StudentDashboardView, StudentProfileUpdateView

app_name = 'students'

urlpatterns = [
    path('dashboard/', StudentDashboardView.as_view(), name='dashboard'),
    path('profile/edit/', StudentProfileUpdateView.as_view(), name='profile_edit'),
]
