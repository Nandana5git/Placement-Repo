from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count
from .models import CompanyProfile
from .forms import CompanyProfileForm
from placements.models import PlacementDrive, Application, InterviewSchedule

class CompanyRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_company

class CompanyDashboardView(LoginRequiredMixin, CompanyRequiredMixin, TemplateView):
    template_name = 'companies/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company_profile

        # Drives
        drives = PlacementDrive.objects.filter(company=company).order_by('-created_at')
        context['drives'] = drives
        context['active_drives_count'] = drives.filter(status=PlacementDrive.Status.ACTIVE).count()

        # Application counts
        apps_query = Application.objects.filter(drive__company=company)
        context['total_applicants'] = apps_query.count()
        context['shortlisted_count'] = apps_query.filter(status=Application.Status.SHORTLISTED).count()
        context['offered_count'] = apps_query.filter(status=Application.Status.OFFERED).count()

        # Hiring Funnel Stage aggregation
        funnel = apps_query.values('current_stage').annotate(count=Count('id'))
        funnel_dict = {stage: 0 for stage, _ in Application.Stage.choices}
        for item in funnel:
            stage_val = item['current_stage']
            if stage_val in funnel_dict:
                funnel_dict[stage_val] = item['count']
        context['funnel_data'] = funnel_dict

        # Upcoming Interviews
        upcoming_interviews = InterviewSchedule.objects.filter(
            application__drive__company=company,
            scheduled_at__gte=timezone.now()
        ).select_related('application__student__user', 'application__drive').order_by('scheduled_at')[:5]
        context['upcoming_interviews'] = upcoming_interviews

        return context


class CompanyProfileUpdateView(LoginRequiredMixin, CompanyRequiredMixin, UpdateView):
    model = CompanyProfile
    form_class = CompanyProfileForm
    template_name = 'companies/profile_update.html'
    success_url = reverse_lazy('companies:dashboard')

    def get_object(self, queryset=None):
        return self.request.user.company_profile
