# Smart College Placement Management Portal - Database Seed Script
import os
import django
import sys
from datetime import datetime, timedelta
from django.utils import timezone

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_portal.settings')
django.setup()

from users.models import User
from students.models import StudentProfile
from companies.models import CompanyProfile
from placements.models import PlacementDrive, Application, InterviewSchedule
from notifications.models import Notification

def seed_database():
    print("Clearing existing data...")
    Notification.objects.all().delete()
    InterviewSchedule.objects.all().delete()
    Application.objects.all().delete()
    PlacementDrive.objects.all().delete()
    StudentProfile.objects.all().delete()
    CompanyProfile.objects.all().delete()
    User.objects.all().delete()

    print("Creating admin/placement officer...")
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@college.edu',
        password='adminpassword',
        first_name='Aditya',
        last_name='Sharma',
        role=User.Role.ADMIN,
        phone_number='9876543210'
    )

    print("Creating companies...")
    # Company 1: Stripe
    stripe_user = User.objects.create_user(
        username='stripe',
        email='hr@stripe.com',
        password='stripepassword',
        first_name='Sarah',
        last_name='Jenkins',
        role=User.Role.COMPANY,
        phone_number='9998887776'
    )
    stripe_profile = CompanyProfile.objects.create(
        user=stripe_user,
        company_name='Stripe',
        website='https://stripe.com',
        hr_name='Sarah Jenkins',
        hr_email='hr@stripe.com',
        hr_phone='9998887776',
        address='Stripe HQ, South Park, San Francisco, CA'
    )

    # Company 2: Google
    google_user = User.objects.create_user(
        username='google',
        email='hr@google.com',
        password='googlepassword',
        first_name='Amit',
        last_name='Patel',
        role=User.Role.COMPANY,
        phone_number='8887776665'
    )
    google_profile = CompanyProfile.objects.create(
        user=google_user,
        company_name='Google India',
        website='https://google.com',
        hr_name='Amit Patel',
        hr_email='hr@google.com',
        hr_phone='8887776665',
        address='Google Signature Tower, Sector 15, Gurugram, India'
    )

    print("Creating students...")
    # Student 1: Eligible CSE student
    s1_user = User.objects.create_user(
        username='student1',
        email='rohit.cse@college.edu',
        password='studentpassword',
        first_name='Rohit',
        last_name='Kumar',
        role=User.Role.STUDENT,
        phone_number='7776665554'
    )
    s1_profile = StudentProfile.objects.create(
        user=s1_user,
        register_number='REG2026CSE001',
        department=StudentProfile.Department.CSE,
        semester=7,
        cgpa=8.85,
        backlogs=0,
        skills='Python, Django, SQL, Git, HTML, CSS, JavaScript'
    )

    # Student 2: ME Student (Ineligible for CSE drives)
    s2_user = User.objects.create_user(
        username='student2',
        email='vijay.me@college.edu',
        password='studentpassword',
        first_name='Vijay',
        last_name='Singh',
        role=User.Role.STUDENT,
        phone_number='6665554443'
    )
    s2_profile = StudentProfile.objects.create(
        user=s2_user,
        register_number='REG2026ME045',
        department=StudentProfile.Department.ME,
        semester=7,
        cgpa=9.12,
        backlogs=0,
        skills='CAD, MATLAB, SolidWorks, Python, Thermodynamics'
    )

    # Student 3: CSE Student with backlogs & low CGPA
    s3_user = User.objects.create_user(
        username='student3',
        email='sneha.cse@college.edu',
        password='studentpassword',
        first_name='Sneha',
        last_name='Rao',
        role=User.Role.STUDENT,
        phone_number='5554443332'
    )
    s3_profile = StudentProfile.objects.create(
        user=s3_user,
        register_number='REG2026CSE089',
        department=StudentProfile.Department.CSE,
        semester=7,
        cgpa=6.45,
        backlogs=2,
        skills='HTML, Java, MySQL'
    )

    print("Creating placement drives...")
    # Stripe Software Engineer Drive
    stripe_drive = PlacementDrive.objects.create(
        company=stripe_profile,
        job_title='Software Development Engineer (SDE-1)',
        job_description='We are looking for enthusiastic SDEs to join our engineering teams. You will work on building scalable API integrations, financial Ledgers, and secure payment processing services.',
        salary_package=14.50,
        eligibility_min_cgpa=7.50,
        eligibility_max_backlogs=0,
        eligible_branches='CSE,IT,AIDS',
        required_skills='Python,Django,SQL',
        drive_date=timezone.now().date() + timedelta(days=5),
        registration_deadline=timezone.now() + timedelta(days=3),
        status=PlacementDrive.Status.ACTIVE
    )

    # Google Systems Engineer Drive
    google_drive = PlacementDrive.objects.create(
        company=google_profile,
        job_title='Systems Test Engineer',
        job_description='Responsible for testing and validating high performance kernel models, memory managers, and android application bundles.',
        salary_package=22.00,
        eligibility_min_cgpa=8.00,
        eligibility_max_backlogs=0,
        eligible_branches='CSE,ECE,IT',
        required_skills='C++,Python',
        drive_date=timezone.now().date() + timedelta(days=10),
        registration_deadline=timezone.now() + timedelta(days=7),
        status=PlacementDrive.Status.ACTIVE
    )

    # Stripe Frontend Dev Drive (Completed/Past)
    stripe_completed_drive = PlacementDrive.objects.create(
        company=stripe_profile,
        job_title='Frontend Integration Intern',
        job_description='Past internship drive for building web application dashboards.',
        salary_package=6.50,
        eligibility_min_cgpa=6.00,
        eligibility_max_backlogs=1,
        eligible_branches='CSE,ECE,IT,AIDS',
        required_skills='JavaScript,HTML',
        drive_date=timezone.now().date() - timedelta(days=15),
        registration_deadline=timezone.now() - timedelta(days=18),
        status=PlacementDrive.Status.COMPLETED
    )

    print("Submitting student applications...")
    # Rohit (student1) applies to Stripe SDE (Eligible)
    app1 = Application.objects.create(
        drive=stripe_drive,
        student=s1_profile,
        status=Application.Status.SHORTLISTED,
        current_stage=Application.Stage.APTITUDE
    )

    # Rohit (student1) applies to Google Systems Eng (Eligible)
    app2 = Application.objects.create(
        drive=google_drive,
        student=s1_profile,
        status=Application.Status.APPLIED,
        current_stage=Application.Stage.APPLIED
    )

    # Rohit (student1) applied to past Stripe Frontend (Eligible) and got offer
    app3 = Application.objects.create(
        drive=stripe_completed_drive,
        student=s1_profile,
        status=Application.Status.OFFERED,
        current_stage=Application.Stage.OFFERED
    )
    s1_profile.placement_status = StudentProfile.PlacementStatus.PLACED
    s1_profile.save()

    print("Scheduling interviews...")
    # Schedule Aptitude test for Rohit with Stripe
    InterviewSchedule.objects.create(
        application=app1,
        round_name=InterviewSchedule.RoundName.APTITUDE,
        scheduled_at=timezone.now() + timedelta(days=1),
        location='Online HackerRank Link',
        notes='Please ensure you have a stable webcam connection. Duration: 90 mins.',
        status=InterviewSchedule.Status.SCHEDULED
    )

    print("Creating notifications...")
    Notification.objects.create(
        user=s1_user,
        title="Application Shortlisted",
        message=f"Congratulations! You have been shortlisted for the Aptitude Test round of {stripe_drive.job_title} at Stripe.",
        is_read=False
    )
    Notification.objects.create(
        user=s1_user,
        title="Interview Scheduled",
        message="Aptitude Test has been scheduled for tomorrow. Check your dashboard timeline.",
        is_read=False
    )

    print("Seeding completed successfully!")
    print("\n--- Mock Credentials ---")
    print("Admin: username='admin', password='adminpassword'")
    print("Stripe Recruiter: username='stripe', password='stripepassword'")
    print("Google Recruiter: username='google', password='googlepassword'")
    print("Rohit (CSE S1): username='student1', password='studentpassword'")
    print("Vijay (ME S2): username='student2', password='studentpassword'")
    print("Sneha (CSE S3): username='student3', password='studentpassword'")
    print("------------------------")

if __name__ == '__main__':
    seed_database()
