from django import forms
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()

class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    phone_number = forms.CharField(max_length=15, required=False, label="Phone Number")

    class Meta:
        model = StudentProfile
        fields = ['register_number', 'department', 'semester', 'cgpa', 'backlogs', 'skills', 'resume', 'profile_photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['phone_number'].initial = self.instance.user.phone_number

        for field_name, field in self.fields.items():
            if field_name not in ['resume', 'profile_photo']:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control-file'

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
            profile.save()
        return profile
