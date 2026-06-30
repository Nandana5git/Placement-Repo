from django.urls import path
from .views import (
    AdminDashboardView, PlacementDriveCreateView, PlacementDriveDetailView,
    ApplyDriveView, UpdateApplicationStageView, InterviewCreateView,
    AdminStudentListView, AdminCompanyListView, AdminDriveListView
)

app_name = 'placements'

urlpatterns = [
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('drive/create/', PlacementDriveCreateView.as_view(), name='drive_create'),
    path('drive/<int:pk>/', PlacementDriveDetailView.as_view(), name='drive_detail'),
    path('drive/<int:pk>/apply/', ApplyDriveView.as_view(), name='apply_drive'),
    path('application/<int:pk>/update/', UpdateApplicationStageView.as_view(), name='update_application'),
    path('application/<int:app_pk>/interview/create/', InterviewCreateView.as_view(), name='interview_create'),
    
    path('students/', AdminStudentListView.as_view(), name='student_list'),
    path('companies/', AdminCompanyListView.as_view(), name='company_list'),
    path('drives/', AdminDriveListView.as_view(), name='drive_list'),
]
