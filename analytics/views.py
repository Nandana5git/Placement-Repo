from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, Http404
import json

from .reports import get_placement_statistics, generate_excel_report
from placements.models import PlacementDrive, Application

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

class AdminAnalyticsDashboard(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = get_placement_statistics()
        context['stats'] = stats
        
        # Serialize statistics for Chart.js
        # 1. Department Charts
        dept_labels = list(stats['dept_placement'].keys())
        dept_rates = [info['rate'] for info in stats['dept_placement'].values()]
        dept_totals = [info['total'] for info in stats['dept_placement'].values()]
        dept_placed = [info['placed'] for info in stats['dept_placement'].values()]
        
        context['dept_chart_labels'] = json.dumps(dept_labels)
        context['dept_chart_rates'] = json.dumps(dept_rates)
        context['dept_chart_totals'] = json.dumps(dept_totals)
        context['dept_chart_placed'] = json.dumps(dept_placed)

        # 2. Company Hiring
        company_labels = list(stats['company_hiring'].keys())
        company_counts = list(stats['company_hiring'].values())
        context['company_chart_labels'] = json.dumps(company_labels)
        context['company_chart_counts'] = json.dumps(company_counts)

        # 3. Monthly Trends
        month_labels = list(stats['monthly_trends'].keys())
        month_counts = list(stats['monthly_trends'].values())
        context['month_chart_labels'] = json.dumps(month_labels)
        context['month_chart_counts'] = json.dumps(month_counts)

        return context


class ExportReportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Security: restrict to Admin or Company
        if not (request.user.is_admin or request.user.is_company):
            return HttpResponse("Unauthorized", status=403)

        report_type = request.GET.get('type')
        drive_id = request.GET.get('drive_id')

        # Company restrictions: Company can only export 'selected_students' and 'company_reports', or their own drive's eligible students
        if request.user.is_company:
            if report_type not in ['selected_students', 'company_reports', 'eligible_students']:
                return HttpResponse("Unauthorized report type", status=403)
            
            if report_type == 'eligible_students' and drive_id:
                drive = get_object_or_404(PlacementDrive, id=drive_id)
                if drive.company != request.user.company_profile:
                    return HttpResponse("Unauthorized to view this drive's candidates", status=403)

        if report_type not in ['eligible_students', 'selected_students', 'company_reports', 'analytics_reports']:
            raise Http404("Report type not found")

        # Generate the Workbook
        wb = generate_excel_report(report_type, drive_id)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{report_type}_{timezone_now_str()}.xlsx"'
        wb.save(response)
        return response

def timezone_now_str():
    from django.utils import timezone
    return timezone.now().strftime('%Y%m%d_%H%M%S')
