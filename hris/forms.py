from django import forms
from .models import employee_detail,CustomUser,department,Leave, Profile

class DateInput(forms.DateInput):
    input_type = 'date'
    
class EmployeeForm(forms.ModelForm):
    empId = forms.CharField()    
    firstName = forms.CharField()
    lastName = forms.CharField()
    midName = forms.CharField()
    birthDate= forms.DateField(widget=DateInput)
    employedDate= forms.DateField(widget=DateInput)
    sex = forms.ChoiceField(widget=forms.RadioSelect, choices=employee_detail.GENDER)
    
    class Meta:
        model = employee_detail
        fields=['user','empId','firstName', "lastName",'midName','birthDate', 'employedDate','sex','phone_number','address','departmentName','positionName','profile_picture']
    

class UserForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'confirm_password', 'email', 'role', 'groups', 'is_staff', 'is_superuser', 'is_active']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        
class DepartmentForm(forms.ModelForm):
    class Meta:
        model=department
        fields='__all__'
        widgets = {
            'departmentName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Name'})
        }


    
class LeaveApplicationForm(forms.ModelForm):
    start_date = forms.DateField(widget=DateInput)
    end_date = forms.DateField(widget=DateInput)
    
    class Meta:
        model=Leave
        fields=['start_date', 'end_date','reason','leave_type']
        widgets = {
            'reason': forms.TextInput(attrs={'size': '40'}),
        }
        
class LeaveApprovalForm(forms.ModelForm):
    class Meta:
        model= Leave
        fields=['status']
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=['hobbies','skills','about']