from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Count, Max, Avg, Q
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import PlacementDrive, Application, InterviewSchedule
from .forms import PlacementDriveForm, InterviewScheduleForm
from .filters import StudentFilter, DriveFilter
from students.models import StudentProfile
from companies.models import CompanyProfile
from notifications.utils import send_system_notification
from users.models import User

# Role verification mixins
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

class AdminOrCompanyRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_admin or self.request.user.is_company


# 1. Admin Dashboard View
class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'placements/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Core KPIs
        total_students = StudentProfile.objects.count()
        total_companies = CompanyProfile.objects.count()
        total_drives = PlacementDrive.objects.count()
        total_offers = Application.objects.filter(status=Application.Status.OFFERED).count()
        
        # Placed student count (either status is PLACED/DREAM or they have an OFFERED application)
        placed_students_count = StudentProfile.objects.filter(
            Q(placement_status__in=[StudentProfile.PlacementStatus.PLACED, StudentProfile.PlacementStatus.DREAM]) |
            Q(applications__status=Application.Status.OFFERED)
        ).distinct().count()

        placement_percentage = int((placed_students_count / total_students * 100)) if total_students > 0 else 0

        context.update({
            'total_students': total_students,
            'total_companies': total_companies,
            'total_drives': total_drives,
            'total_offers': total_offers,
            'placement_percentage': placement_percentage,
        })

        # Drive timelines
        context['upcoming_drives'] = PlacementDrive.objects.filter(
            drive_date__gte=timezone.now().date()
        ).select_related('company').order_by('drive_date')[:5]

        # Recent activities
        recent_applications = Application.objects.select_related('student__user', 'drive__company').order_by('-applied_at')[:4]
        activities = []
        for app in recent_applications:
            activities.append({
                'type': 'application',
                'title': f"{app.student.user.get_full_name()} applied to {app.drive.job_title}",
                'subtitle': f"Company: {app.drive.company.company_name}",
                'timestamp': app.applied_at
            })
        
        recent_interviews = InterviewSchedule.objects.select_related('application__student__user', 'application__drive').order_by('-created_at')[:4]
        for interview in recent_interviews:
            activities.append({
                'type': 'interview',
                'title': f"Interview Scheduled ({interview.get_round_name_display()})",
                'subtitle': f"Student: {interview.application.student.user.get_full_name()} for {interview.application.drive.job_title}",
                'timestamp': interview.created_at
            })
            
        activities = sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:5]
        context['recent_activities'] = activities

        return context


# 2. Drive Create View
class PlacementDriveCreateView(LoginRequiredMixin, AdminOrCompanyRequiredMixin, CreateView):
    model = PlacementDrive
    form_class = PlacementDriveForm
    template_name = 'placements/drive_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_company:
            form.instance.company = self.request.user.company_profile
        response = super().form_valid(form)
        
        # Notify all students who are eligible for this new drive
        eligible_students = StudentProfile.objects.all()
        for student in eligible_students:
            eligible, _ = self.object.is_eligible(student)
            if eligible:
                send_system_notification(
                    user=student.user,
                    title="New Eligible Placement Drive",
                    message=f"A new drive '{self.object.job_title}' has been announced by {self.object.company.company_name}. Register before the deadline: {self.object.registration_deadline.strftime('%d-%b-%Y %I:%M %p')}.",
                    send_email=True
                )
        return response

    def get_success_url(self):
        return reverse('placements:drive_detail', kwargs={'pk': self.object.pk})


# 3. Drive Detail View
class PlacementDriveDetailView(LoginRequiredMixin, DetailView):
    model = PlacementDrive
    template_name = 'placements/drive_detail.html'
    context_object_name = 'drive'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        drive = self.object

        if user.is_student:
            student = user.student_profile
            # Check application status
            application = Application.objects.filter(drive=drive, student=student).first()
            context['application'] = application
            
            # Check eligibility
            eligible, reason = drive.is_eligible(student)
            context['is_eligible'] = eligible
            context['eligibility_reason'] = reason
            context['has_deadline_passed'] = timezone.now() > drive.registration_deadline
        else:
            # For admin and company, fetch candidates and applicants
            apps = drive.applications.select_related('student__user').order_by('-applied_at')
            context['applications'] = apps
            context['applied_count'] = apps.filter(status=Application.Status.APPLIED).count()
            context['shortlisted_count'] = apps.filter(status=Application.Status.SHORTLISTED).count()
            context['offered_count'] = apps.filter(status=Application.Status.OFFERED).count()
            context['rejected_count'] = apps.filter(status=Application.Status.REJECTED).count()

        return context


# 4. Apply Drive View
class ApplyDriveView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_student:
            messages.error(request, "Only students can apply to placement drives.")
            return redirect('login')

        drive = get_object_or_404(PlacementDrive, pk=pk)
        student = request.user.student_profile

        # Deadline check
        if timezone.now() > drive.registration_deadline:
            messages.error(request, "Registration deadline for this drive has passed.")
            return redirect('placements:drive_detail', pk=pk)

        # Eligibility check
        eligible, reason = drive.is_eligible(student)
        if not eligible:
            messages.error(request, f"You are not eligible to apply. Reason: {reason}")
            return redirect('placements:drive_detail', pk=pk)

        # Check existing application
        if Application.objects.filter(drive=drive, student=student).exists():
            messages.info(request, "You have already registered for this drive.")
            return redirect('placements:drive_detail', pk=pk)

        # Create Application
        application = Application.objects.create(drive=drive, student=student)
        
        # Notify student & company
        send_system_notification(
            user=request.user,
            title="Application Submitted",
            message=f"You successfully applied for {drive.job_title} at {drive.company.company_name}.",
            send_email=True
        )

        send_system_notification(
            user=drive.company.user,
            title="New Application Received",
            message=f"Student {student.user.get_full_name()} ({student.register_number}) has applied for {drive.job_title}.",
            send_email=False
        )

        messages.success(request, f"Successfully applied for {drive.job_title}!")
        return redirect('placements:drive_detail', pk=pk)


# 5. Update Application Stage & Status
class UpdateApplicationStageView(LoginRequiredMixin, AdminOrCompanyRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        application = get_object_or_404(Application, pk=pk)
        status = request.POST.get('status')
        stage = request.POST.get('stage')

        old_status = application.status
        old_stage = application.current_stage

        if status:
            application.status = status
        if stage:
            application.current_stage = stage
        application.save()

        # Update student profile placement status automatically if offered
        if application.status == Application.Status.OFFERED:
            student = application.student
            if application.drive.salary_package >= 10.00:
                student.placement_status = StudentProfile.PlacementStatus.DREAM
            else:
                student.placement_status = StudentProfile.PlacementStatus.PLACED
            student.save()

        # Notify student on update
        if old_status != application.status or old_stage != application.current_stage:
            send_system_notification(
                user=application.student.user,
                title="Application Status Updated",
                message=f"Your application for {application.drive.job_title} at {application.drive.company.company_name} has been updated. Status: {application.get_status_display()}, Recruitment Round: {application.get_current_stage_display()}.",
                send_email=True
            )

        messages.success(request, "Applicant status updated successfully.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('placements:drive_detail', kwargs={'pk': application.drive.pk})))


# 6. Interview Create View
class InterviewCreateView(LoginRequiredMixin, AdminOrCompanyRequiredMixin, CreateView):
    model = InterviewSchedule
    form_class = InterviewScheduleForm
    template_name = 'placements/interview_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.application = get_object_or_404(Application, pk=self.kwargs.get('app_pk'))
        return kwargs

    def form_valid(self, form):
        form.instance.application = self.application
        response = super().form_valid(form)

        # Notify student about interview
        send_system_notification(
            user=self.application.student.user,
            title="Interview Round Scheduled",
            message=f"An interview round ({form.instance.get_round_name_display()}) has been scheduled for your application with {self.application.drive.company.company_name}.\nDate & Time: {form.instance.scheduled_at.strftime('%d-%b-%Y %I:%M %p')}\nVenue/Link: {form.instance.location}\nNotes: {form.instance.notes or 'N/A'}",
            send_email=True
        )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        return context

    def get_success_url(self):
        return reverse('placements:drive_detail', kwargs={'pk': self.application.drive.pk})


# 7. Lists: Student directory, Companies directory, Drive directory
class AdminStudentListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = StudentProfile
    template_name = 'placements/student_list.html'
    context_object_name = 'students'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        self.filterset = StudentFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class AdminCompanyListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CompanyProfile
    template_name = 'placements/company_list.html'
    context_object_name = 'companies'
    paginate_by = 25


class AdminDriveListView(LoginRequiredMixin, ListView):
    model = PlacementDrive
    template_name = 'placements/drive_list.html'
    context_object_name = 'drives'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company')
        # If user is company, limit drives
        if self.request.user.is_company:
            queryset = queryset.filter(company=self.request.user.company_profile)
        self.filterset = DriveFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context
