from django import forms
from .models import PlacementDrive, InterviewSchedule, Application
from companies.models import CompanyProfile

class PlacementDriveForm(forms.ModelForm):
    class Meta:
        model = PlacementDrive
        fields = [
            'company', 'job_title', 'job_description', 'salary_package',
            'eligibility_min_cgpa', 'eligibility_max_backlogs',
            'eligible_branches', 'required_skills', 'drive_date',
            'registration_deadline', 'status'
        ]
        widgets = {
            'drive_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'job_description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'eligible_branches': forms.TextInput(attrs={'placeholder': 'e.g. CSE, ECE, IT', 'class': 'form-control'}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'e.g. Python, SQL', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is a company, lock company field and exclude/hide it or prefill it
        if user and user.is_company:
            self.fields['company'].queryset = CompanyProfile.objects.filter(user=user)
            self.fields['company'].initial = user.company_profile
            self.fields['company'].widget = forms.HiddenInput()
        else:
            self.fields['company'].queryset = CompanyProfile.objects.all()
            self.fields['company'].widget.attrs['class'] = 'form-select'
            
        for name, field in self.fields.items():
            if name not in ['drive_date', 'registration_deadline', 'company', 'job_description', 'eligible_branches', 'required_skills']:
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'


class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = InterviewSchedule
        fields = ['round_name', 'scheduled_at', 'location', 'notes', 'status']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ['scheduled_at', 'notes']:
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'
