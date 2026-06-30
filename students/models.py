from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    class Department(models.TextChoices):
        CSE = 'CSE', 'Computer Science & Engineering'
        ECE = 'ECE', 'Electronics & Communication Engineering'
        EEE = 'EEE', 'Electrical & Electronics Engineering'
        ME = 'ME', 'Mechanical Engineering'
        CE = 'CE', 'Civil Engineering'
        IT = 'IT', 'Information Technology'
        AIDS = 'AIDS', 'AI & Data Science'

    class PlacementStatus(models.TextChoices):
        UNPLACED = 'UNPLACED', 'Unplaced'
        PLACED = 'PLACED', 'Placed'
        DREAM = 'DREAM', 'Dream Placed'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    register_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=10, choices=Department.choices)
    semester = models.PositiveSmallIntegerField(default=1)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    backlogs = models.PositiveSmallIntegerField(default=0)
    skills = models.TextField(blank=True, help_text="Comma-separated skills (e.g. Python, SQL, Django)")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    placement_status = models.CharField(
        max_length=15,
        choices=PlacementStatus.choices,
        default=PlacementStatus.UNPLACED
    )

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.register_number})"

    @property
    def skill_list(self):
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
