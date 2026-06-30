from django.db import models
from django.conf import settings
from companies.models import CompanyProfile
from students.models import StudentProfile

class PlacementDrive(models.Model):
    class Status(models.TextChoices):
        UPCOMING = 'UPCOMING', 'Upcoming'
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='drives'
    )
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()
    salary_package = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Salary package in LPA (Lakhs Per Annum), e.g. 12.50"
    )
    eligibility_min_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=6.00,
        help_text="Minimum CGPA required"
    )
    eligibility_max_backlogs = models.PositiveSmallIntegerField(
        default=0,
        help_text="Maximum active backlogs allowed"
    )
    eligible_branches = models.TextField(
        help_text="Comma-separated eligible branches (e.g. CSE, ECE, IT)"
    )
    required_skills = models.TextField(
        blank=True,
        help_text="Comma-separated required skills (e.g. Python, SQL)"
    )
    drive_date = models.DateField()
    registration_deadline = models.DateTimeField()
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} at {self.company.company_name}"

    def is_eligible(self, student):
        # 1. CGPA Check
        if student.cgpa < self.eligibility_min_cgpa:
            return False, f"CGPA too low. Required: {self.eligibility_min_cgpa}, Current: {student.cgpa}"

        # 2. Backlog Check
        if student.backlogs > self.eligibility_max_backlogs:
            return False, f"Backlogs exceed limit. Allowed: {self.eligibility_max_backlogs}, Current: {student.backlogs}"

        # 3. Branch/Department Check
        if self.eligible_branches:
            branches = [b.strip().upper() for b in self.eligible_branches.split(',') if b.strip()]
            if student.department.upper() not in branches:
                return False, f"Department '{student.get_department_display()}' is not eligible."

        # 4. Required Skills Check (at least one matching skill)
        if self.required_skills:
            req_skills = [s.strip().lower() for s in self.required_skills.split(',') if s.strip()]
            student_skills = [s.lower() for s in student.skill_list]
            if req_skills and not any(s in student_skills for s in req_skills):
                return False, f"Missing required skills. Required: {self.required_skills}"

        return True, "Eligible"


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = 'APPLIED', 'Applied'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        REJECTED = 'REJECTED', 'Rejected'
        OFFERED = 'OFFERED', 'Offered'

    class Stage(models.TextChoices):
        APPLIED = 'APPLIED', 'Applied'
        APTITUDE = 'APTITUDE', 'Aptitude Test'
        TECHNICAL = 'TECHNICAL', 'Technical Interview'
        HR = 'HR', 'HR Interview'
        OFFERED = 'OFFERED', 'Offered'
        REJECTED = 'REJECTED', 'Rejected'

    drive = models.ForeignKey(
        PlacementDrive,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED
    )
    current_stage = models.CharField(
        max_length=20,
        choices=Stage.choices,
        default=Stage.APPLIED
    )

    class Meta:
        unique_together = ('drive', 'student')

    def __str__(self):
        return f"{self.student} - {self.drive}"


class InterviewSchedule(models.Model):
    class RoundName(models.TextChoices):
        APTITUDE = 'APTITUDE', 'Aptitude Test'
        TECHNICAL = 'TECHNICAL', 'Technical Interview'
        HR = 'HR', 'HR Interview'
        OTHER = 'OTHER', 'Other Round'

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        RESCHEDULED = 'RESCHEDULED', 'Rescheduled'
        CANCELLED = 'CANCELLED', 'Cancelled'

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    round_name = models.CharField(
        max_length=20,
        choices=RoundName.choices,
        default=RoundName.APTITUDE
    )
    scheduled_at = models.DateTimeField()
    location = models.CharField(
        max_length=255,
        help_text="Venue name or Video Call link"
    )
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_round_name_display()} for {self.application.student.user.get_full_name()} - {self.status}"
