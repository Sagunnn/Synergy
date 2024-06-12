from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
import uuid
from django import forms
import datetime


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("HR", "Human Resources"),
        ("EMPLOYEE", "Employee"),
        ("ADMIN", "Administrator"),
        ("MANAGER", "Manager"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="EMPLOYEE")
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # New user being created, set the password
            self.set_password(self.password)
        return super().save(*args, **kwargs)


class employee_detail(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    empId = models.CharField(max_length=20,primary_key=True)    
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    midName = models.CharField(max_length=50,null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures',default='default_profile.jpg')
    def get_full_name(self):
        if self.midName is None:
            return f"{self.firstName} {self.lastName}".strip()
        else:
            return f"{self.firstName} {self.midName} {self.lastName}".strip()
    
    positionName = models.ForeignKey("positions", on_delete=models.SET_NULL,null=True)
    departmentName = models.ForeignKey("department", on_delete=models.SET_NULL,null=True)
    birthDate = models.DateField()
    
    GENDER= [
        ("M", "Male"),
        ("F", "Female"),
        ("O","Other"),
    ]
    sex = models.CharField(max_length=20,choices=GENDER)
    address = models.CharField(max_length=100)
    phone_number= models.CharField(max_length=14)
    employedDate = models.DateField()
    sick_leave_balance = models.PositiveIntegerField(default=7)
    paid_leave_balance = models.PositiveIntegerField(default=15)
    unpaid_leave_balance = models.PositiveIntegerField(default=7)
    
    def get_fields(self):
        # Exclude fields that are not required for table creation
        excluded_fields = ["id", "user"]

        # Get all model fields
        fields = self._meta.fields

        # Filter fields based on the excluded fields list
        filtered_fields = [field for field in fields if field.name not in excluded_fields]

        return filtered_fields

    @classmethod
    def get_field_names(cls):
        """Get the names of all fields except excluded fields."""
        excluded_fields = ["id", "user"]
        field_names = [field.name for field in cls._meta.fields if field.name not in excluded_fields]
        return field_names
    
    def __str__(self):
        return self.empId



class positions(models.Model):
    positionName = models.CharField(max_length=50)
    
    def __str__(self):
        return self.positionName


class department(models.Model):
    departmentName = models.CharField(max_length=100)
    
    def __str__(self):
        return self.departmentName


class Leave(models.Model):
    leave_id = models.AutoField(primary_key=True)
    empId=models.ForeignKey(employee_detail,on_delete=models.CASCADE)
    start_date=models.DateField()
    end_date=models.DateField()
    reason=models.TextField()
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    LEAVE_TYPE_CHOICES = (
        ('sick_leave', 'Sick Leave'),
        ('paid_leave', 'Paid Leave'),
        ('unpaid_leave', 'Unpaid Leave'),
        ('maternity', 'Maternity'),
        # Add more leave types as needed
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES,default='unpaid_leave')
    
    def __str__(self):
        return str(self.leave_id)
    
    @property
    def duration(self):
        # Calculate and return the duration of the leave in days
        return ((self.end_date - self.start_date).days+1)
    
    def get_leave_type_display(self):
        return dict(self.LEAVE_TYPE_CHOICES)[self.leave_type]
    
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    hobbies = models.CharField(max_length=100)
    skills= models.CharField(max_length=100)
    about=models.CharField(max_length=500)
    

class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField()
    duration = models.DurationField(null=True, blank=True)

    def save(self, *args, **kwargs):
        time1 = datetime.datetime.strptime(self.time_in,'%H:%M')
        time2 = datetime.datetime.strptime(self.time_out,'%H:%M')
        difference = time2-time1
        print (difference)
        self.duration=difference
        super().save(*args, **kwargs)