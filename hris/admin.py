from django.contrib import admin
from .models import CustomUser, employee_detail, Leave, department, positions


admin.site.register(CustomUser)
admin.site.register(employee_detail)
admin.site.register(Leave)
admin.site.register(department)
admin.site.register(positions)

# Register your models here.
