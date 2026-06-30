from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, RedirectView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import StudentRegistrationForm, CompanyRegistrationForm, BootstrapLoginForm
from .models import User

class StudentRegisterView(CreateView):
    model = User
    form_class = StudentRegistrationForm
    template_name = 'registration/register_student.html'
    success_url = reverse_lazy('dashboard_router')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in after registration
        login(self.request, self.object)
        return response


class CompanyRegisterView(CreateView):
    model = User
    form_class = CompanyRegistrationForm
    template_name = 'registration/register_company.html'
    success_url = reverse_lazy('dashboard_router')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in after registration
        login(self.request, self.object)
        return response


class BootstrapLoginView(LoginView):
    authentication_form = BootstrapLoginForm
    template_name = 'registration/login.html'


class DashboardRouterView(LoginRequiredMixin, RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return reverse_lazy('students:dashboard')
        elif user.role == User.Role.COMPANY:
            return reverse_lazy('companies:dashboard')
        elif user.role == User.Role.ADMIN:
            return reverse_lazy('placements:admin_dashboard')
        return reverse_lazy('login')
