from django import forms
from django.contrib.auth import get_user_model
from .models import CompanyProfile

User = get_user_model()

class CompanyProfileForm(forms.ModelForm):
    hr_email = forms.EmailField(required=True, label="HR Contact Email")
    hr_phone = forms.CharField(max_length=15, required=True, label="HR Contact Phone")

    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'logo', 'website', 'hr_name', 'hr_email', 'hr_phone', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'logo':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control-file'

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.email = self.cleaned_data['hr_email']
        user.phone_number = self.cleaned_data['hr_phone']
        if commit:
            user.save()
            profile.save()
        return profile
