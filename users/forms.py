from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from students.models import StudentProfile
from companies.models import CompanyProfile

User = get_user_model()

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    register_number = forms.CharField(max_length=20, required=True, label="Register Number")
    department = forms.ChoiceField(choices=StudentProfile.Department.choices, required=True, label="Department")
    semester = forms.IntegerField(min_value=1, max_value=8, required=True, label="Current Semester")
    cgpa = forms.DecimalField(max_digits=4, decimal_places=2, min_value=0.00, max_value=10.00, required=True, label="CGPA")
    backlogs = forms.IntegerField(min_value=0, required=True, label="Active Backlogs")
    skills = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Skills (comma-separated)", help_text="e.g. Python, SQL, Django")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control rounded-pill-sm'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                register_number=self.cleaned_data['register_number'],
                department=self.cleaned_data['department'],
                semester=self.cleaned_data['semester'],
                cgpa=self.cleaned_data['cgpa'],
                backlogs=self.cleaned_data['backlogs'],
                skills=self.cleaned_data['skills']
            )
        return user


class CompanyRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=100, required=True, label="Company Name")
    website = forms.URLField(required=False, label="Company Website")
    hr_name = forms.CharField(max_length=100, required=True, label="HR Contact Name")
    hr_email = forms.EmailField(required=True, label="HR Contact Email")
    hr_phone = forms.CharField(max_length=15, required=True, label="HR Contact Phone")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Office Address")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.COMPANY
        # Use company email as user email
        user.email = self.cleaned_data['hr_email']
        if commit:
            user.save()
            CompanyProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                website=self.cleaned_data['website'],
                hr_name=self.cleaned_data['hr_name'],
                hr_email=self.cleaned_data['hr_email'],
                hr_phone=self.cleaned_data['hr_phone'],
                address=self.cleaned_data['address']
            )
        return user


class BootstrapLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
