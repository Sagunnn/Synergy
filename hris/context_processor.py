from django.contrib.auth import get_user_model
from .models import CustomUser,employee_detail

User = get_user_model()

def employee_name(request):
    user = request.user
    if isinstance(user, User):
        try:
            employee = user.employee
            employee_name = f"{employee.firstName} {employee.lastName}"
        except employee_detail.DoesNotExist:
            employee_name = None
    else:
        employee_name = None
    return {'employee_name': employee_name}