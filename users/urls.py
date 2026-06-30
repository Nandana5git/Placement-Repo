from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import StudentRegisterView, CompanyRegisterView, BootstrapLoginView, DashboardRouterView

urlpatterns = [
    path('login/', BootstrapLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/student/', StudentRegisterView.as_view(), name='register_student'),
    path('register/company/', CompanyRegisterView.as_view(), name='register_company'),
    path('dashboard/', DashboardRouterView.as_view(), name='dashboard_router'),
]
