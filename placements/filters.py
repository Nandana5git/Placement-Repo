import django_filters
from students.models import StudentProfile
from .models import PlacementDrive

class StudentFilter(django_filters.FilterSet):
    min_cgpa = django_filters.NumberFilter(field_name='cgpa', lookup_expr='gte', label='Min CGPA')
    max_backlogs = django_filters.NumberFilter(field_name='backlogs', lookup_expr='lte', label='Max Backlogs')
    department = django_filters.ChoiceFilter(field_name='department', choices=StudentProfile.Department.choices, label='Branch')
    skills = django_filters.CharFilter(field_name='skills', lookup_expr='icontains', label='Skills (Contains)')
    placement_status = django_filters.ChoiceFilter(field_name='placement_status', choices=StudentProfile.PlacementStatus.choices, label='Placement Status')

    class Meta:
        model = StudentProfile
        fields = ['department', 'placement_status']


class DriveFilter(django_filters.FilterSet):
    min_package = django_filters.NumberFilter(field_name='salary_package', lookup_expr='gte', label='Min Package (LPA)')
    status = django_filters.ChoiceFilter(field_name='status', choices=PlacementDrive.Status.choices, label='Status')

    class Meta:
        model = PlacementDrive
        fields = ['status']
