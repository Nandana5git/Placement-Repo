from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from users.models import User
from students.models import StudentProfile
from companies.models import CompanyProfile
from placements.models import PlacementDrive, Application, InterviewSchedule
from analytics.reports import get_placement_statistics, generate_excel_report

class PlacementPortalTestCase(TestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            username='admin_test', email='adm@test.com', password='pw', role=User.Role.ADMIN
        )
        self.stripe_user = User.objects.create_user(
            username='stripe_test', email='stripe@test.com', password='pw', role=User.Role.COMPANY
        )
        self.s1_user = User.objects.create_user(
            username='s1_test', email='s1@test.com', password='pw', role=User.Role.STUDENT
        )
        self.s2_user = User.objects.create_user(
            username='s2_test', email='s2@test.com', password='pw', role=User.Role.STUDENT
        )
        self.s3_user = User.objects.create_user(
            username='s3_test', email='s3@test.com', password='pw', role=User.Role.STUDENT
        )

        # Profiles
        self.stripe_company = CompanyProfile.objects.create(
            user=self.stripe_user, company_name="Stripe"
        )
        
        self.s1_student = StudentProfile.objects.create(
            user=self.s1_user, register_number="REG001", department=StudentProfile.Department.CSE,
            semester=7, cgpa=8.50, backlogs=0, skills="Python, SQL, Django"
        )
        self.s2_student = StudentProfile.objects.create(
            user=self.s2_user, register_number="REG002", department=StudentProfile.Department.ME,
            semester=7, cgpa=9.00, backlogs=0, skills="Python"
        )
        self.s3_student = StudentProfile.objects.create(
            user=self.s3_user, register_number="REG003", department=StudentProfile.Department.CSE,
            semester=7, cgpa=6.00, backlogs=2, skills="HTML"
        )

        # Drive
        self.drive = PlacementDrive.objects.create(
            company=self.stripe_company,
            job_title="Software Engineer",
            job_description="Description",
            salary_package=12.00,
            eligibility_min_cgpa=7.50,
            eligibility_max_backlogs=0,
            eligible_branches="CSE, IT",
            required_skills="Python, SQL",
            drive_date=timezone.now().date() + timedelta(days=2),
            registration_deadline=timezone.now() + timedelta(days=1),
            status=PlacementDrive.Status.ACTIVE
        )

    def test_user_roles(self):
        """Verify custom user role helpers work correctly."""
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.admin.is_student)
        
        self.assertTrue(self.stripe_user.is_company)
        self.assertFalse(self.stripe_user.is_admin)
        
        self.assertTrue(self.s1_user.is_student)
        self.assertFalse(self.s1_user.is_company)

    def test_drive_eligibility(self):
        """Verify the eligibility check handles branch, cgpa, backlogs, and skills."""
        # 1. Rohit (S1): CSE, 8.5 CGPA, 0 backlogs, skills overlaps -> Eligible
        eligible, reason = self.drive.is_eligible(self.s1_student)
        self.assertTrue(eligible, f"Rohit should be eligible: {reason}")

        # 2. Vijay (S2): ME, 9.0 CGPA, 0 backlogs, skills overlaps -> Ineligible (wrong Branch)
        eligible, reason = self.drive.is_eligible(self.s2_student)
        self.assertFalse(eligible)
        self.assertIn("not eligible", reason.lower())

        # 3. Sneha (S3): CSE, 6.0 CGPA, 2 backlogs -> Ineligible (low CGPA & backlogs)
        eligible, reason = self.drive.is_eligible(self.s3_student)
        self.assertFalse(eligible)
        self.assertIn("cgpa too low", reason.lower())

    def test_pandas_statistics(self):
        """Verify that pandas compiles placement percentages and averages correctly."""
        # Setup selection
        Application.objects.create(
            drive=self.drive, student=self.s1_student, status=Application.Status.OFFERED, current_stage=Application.Stage.OFFERED
        )
        self.s1_student.placement_status = StudentProfile.PlacementStatus.PLACED
        self.s1_student.save()

        stats = get_placement_statistics()
        
        # 1 out of 3 students placed = 33%
        self.assertEqual(stats['total_students'], 3)
        self.assertEqual(stats['placement_percentage'], 33)
        self.assertEqual(stats['highest_package'], 12.0)
        self.assertEqual(stats['average_package'], 12.0)
        self.assertEqual(stats['company_hiring']['Stripe'], 1)

    def test_excel_export(self):
        """Verify OpenPyXL report generation completes without exceptions."""
        wb_eligible = generate_excel_report('eligible_students', drive_id=self.drive.id)
        wb_selected = generate_excel_report('selected_students')
        wb_company = generate_excel_report('company_reports')
        wb_analytics = generate_excel_report('analytics_reports')

        self.assertIsNotNone(wb_eligible)
        self.assertIsNotNone(wb_selected)
        self.assertIsNotNone(wb_company)
        self.assertIsNotNone(wb_analytics)
        
        self.assertEqual(wb_eligible.active.title, "Eligible Students")
        self.assertEqual(wb_selected.active.title, "Selected Students")
        self.assertEqual(wb_company.active.title, "Company Drives Summary")
        self.assertEqual(wb_analytics.active.title, "Overview Statistics")
