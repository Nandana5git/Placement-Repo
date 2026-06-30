from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from .models import StudentProfile
from .forms import StudentProfileForm
from placements.models import PlacementDrive, Application, InterviewSchedule
from notifications.models import Notification

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_student

class StudentDashboardView(LoginRequiredMixin, StudentRequiredMixin, TemplateView):
    template_name = 'students/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # 1. Profile Completion Percentage
        profile_fields = [
            student.user.first_name,
            student.user.last_name,
            student.user.email,
            student.user.phone_number,
            student.register_number,
            student.skills,
            student.resume,
            student.profile_photo,
        ]
        filled = sum(1 for field in profile_fields if field)
        completion_percentage = int((filled / len(profile_fields)) * 100)
        context['completion_percentage'] = completion_percentage

        # 2. Applied Companies / Applications
        applications = Application.objects.filter(student=student).select_related('drive', 'drive__company')
        context['applications'] = applications
        context['applied_count'] = applications.count()

        # 3. Upcoming Interviews
        upcoming_interviews = InterviewSchedule.objects.filter(
            application__student=student,
            scheduled_at__gte=timezone.now()
        ).select_related('application__drive', 'application__drive__company').order_name = 'scheduled_at'
        # Wait, the above line says order_name = 'scheduled_at' which is a typo, it should be order_by('scheduled_at')
        
        # Let's fix that order_by
        upcoming_interviews = InterviewSchedule.objects.filter(
            application__student=student,
            scheduled_at__gte=timezone.now()
        ).select_related('application__drive', 'application__drive__company').order_by('scheduled_at')
        context['upcoming_interviews'] = upcoming_interviews

        # 4. Offers
        offers = applications.filter(status=Application.Status.OFFERED)
        context['offers'] = offers

        # 5. Recent Notifications
        notifications = Notification.objects.filter(user=self.request.user)[:5]
        context['recent_notifications'] = notifications

        # 6. Recommended Companies (Active drives where student is eligible and hasn't applied)
        applied_drive_ids = applications.values_list('drive_id', flat=True)
        active_drives = PlacementDrive.objects.filter(status=PlacementDrive.Status.ACTIVE).exclude(id__in=applied_drive_ids).select_related('company')
        
        recommended_drives = []
        for drive in active_drives:
            eligible, _ = drive.is_eligible(student)
            if eligible:
                recommended_drives.append(drive)
        context['recommended_drives'] = recommended_drives[:4]

        return context


class StudentProfileUpdateView(LoginRequiredMixin, StudentRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'students/profile_update.html'
    success_url = reverse_lazy('students:dashboard')

    def get_object(self, queryset=None):
        return self.request.user.student_profile
