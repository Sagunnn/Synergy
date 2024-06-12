from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import department,employee_detail,CustomUser,Leave,Profile,Attendance
from .forms import EmployeeForm,UserForm,DepartmentForm,LeaveApplicationForm,LeaveApprovalForm, ProfileForm, ProfilePic,AttendanceForm
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
import traceback
from datetime import date,timedelta
from django.urls import reverse
from django.contrib.auth import logout
from django.http import JsonResponse
from django.db.models import Sum




def home(request):
    objs=employee_detail.objects.all()
    for employee in objs:
        print(employee.lastName)
    return render(request,"homepage.html")

@login_required
def profile(request):
    if request.user.is_authenticated: 
        try:
            objs = employee_detail.objects.filter(user=request.user)
            # Print the usernames of the employee_detail objects
            for obj in objs:
                print('Employee username:', obj.user.username)
            obj = objs.first()
            infos=Profile.objects.filter(user=request.user)
            info=infos.first()
            if obj:
                return render(request, './components/profile.html', {'obj': obj,'info': info})
            else:
                print('No matching employee_detail object for the user')
                return redirect('dashboard')
        except employee_detail.DoesNotExist:
            print('does not exist')
            return redirect('dashboard')
        
@login_required
def change_profile(request):
    if request.user.is_authenticated:
        update_record=employee_detail.objects.get(user=request.user)
        profile = employee_detail.objects.get(user=request.user)
        
        if request.method=="POST":
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            return redirect('profile')
        else:
                form = ProfilePic(instance=update_record)
        return render(request,"./components/update_pp.html",{'form':form})
    else:
        messages.error(request,"Not authorized to update")
        return redirect('profile')

@login_required
def profile_update(request):
    if request.user.is_authenticated:
        try:
            update_profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            update_profile = None

        if request.method == "POST":
            form = ProfileForm(request.POST, instance=update_profile)
            update_profile = Profile.objects.get(user=request.user)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.id=update_profile.id
                profile.user = request.user
                profile.save()
                messages.success(request, "Profile updated successfully")
                return redirect('profile')
        else:
            form = ProfileForm(instance=update_profile)
        
        return render(request, "./components/update_profile.html", {'form': form})
    else:
        messages.error(request, "Not authorized to update")
        return redirect('profile')

def auto_logout(request):
    logout(request)
    return JsonResponse({'status': 'logged out'})

def login_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("Hello")
            login(request, user)
            messages.success(request, f"Logged in successfully. Welcome {user.employee_detail.get_full_name()}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, "components/login.html")

def logout_user(request):
    logout(request)
    return redirect('login')

def demo(request):
    return render(request, "demo.html")

def get_total_hours_this_week(user):
    """
    Calculates the total hours worked by the given user in the current week.
    """
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    total_hours_this_week = Attendance.objects.filter(
        user=user,
        date__range=[start_of_week, end_of_week]
    ).aggregate(total_hours=Sum('duration'))['total_hours']

    return total_hours_this_week or 0 

@login_required
def dashboard(request):
    employee_count = employee_detail.objects.count()
    department_count = department.objects.count()
    today = date.today()
    leaves_count = Leave.objects.filter(start_date__lte=today, end_date__gte=today, status = 'approved').count()
    total_hours_this_week = get_total_hours_this_week(request.user)
    # Prepare the context dictionary
    context = {
        'employee_count': employee_count,
        'department_count': department_count,
        'total_hours_this_week': total_hours_this_week,
        'leaves_count': leaves_count,
    }
    return render(request, './components/dashboard.html', context)
    
#employees modules
@login_required
def employees(request):
    objs=employee_detail.objects.all()
    for employee in objs:
        print(employee.lastName)         
    return render(request, './components/employees.html',{'objs':objs,'user':request.user})
"""
@login_required
def employee_delete(request, pk):
    if request.user.is_authenticated and request.user.role in ['ADMIN', 'HR']:
        try:
            employee = employee_detail.objects.get(empId=pk)
            user = employee.user
            user.delete()
            employee.delete()
            messages.success(request, "Employee deleted successfully.")
        except (employee_detail.DoesNotExist, CustomUser.DoesNotExist):
            messages.error(request, "Employee not found.")
        except Exception as e:
            messages.error(request, f"Error deleting employee: {e}")
    else:
        messages.error(request, "Not authorized to delete employees.")
    return redirect('employees')
"""
@login_required
def employee_delete(request, pk):
    if request.user.is_authenticated and request.user.role in ['ADMIN', 'HR']:
        try:
            employee_delete = employee_detail.objects.get(empId=pk)
        except employee_detail.DoesNotExist:
            messages.error(request, "Employee does not exist.")
            return redirect('employees')
        if request.method== 'POST':
            try:
                user=employee_delete.user
                user.delete()
                employee_delete.delete()
                messages.success(request, "Employee deleted successfully.")
                return redirect('employees')
            except Exception as e:
                messages.error(request, f"Error deleting Employee: {e}")
                return redirect('employees')
        else:
            employee_delete = employee_detail.objects.get(empId=pk)
            return render(request, "./components/employee_delete.html", {'employee': employee_delete})
    else:
        messages.error(request, "Error")
        return redirect('employees')

@login_required
def employee_record(request,pk):
    if request.user.is_authenticated:
        employee_record=employee_detail.objects.get(empId=pk)
        userx=employee_record.user
        try:
            info = Profile.objects.get(user=userx)
        except Profile.DoesNotExist:
            info = None
        if info is not None:
            return render(request,"./components/employee_record.html",{'employee_record':employee_record,'info':info})
        else:
            return render(request,"./components/employee_record.html",{'employee_record':employee_record})

@login_required
def update_record(request,pk):
    if request.user.is_authenticated and request.user.role in ['ADMIN','HR']:
        if request.user.role == 'ADMIN' or request.user.empId ==pk:
            update_record=employee_detail.objects.get(empId=pk)
            user=update_record.user
            if request.method=="POST":
                form = EmployeeForm(request.POST, request.FILES,instance=update_record)
                print(user)
                if form.is_valid():
                    print(user)
                    form.instance.user = user
                    form.save()
                    messages.success(request,"Employee record updated successfully")
                    return redirect('employees')
            else:
                form = EmployeeForm(instance=update_record)
            return render(request,"./components/update_record.html",{'form':form})
        messages.error(request,"Not authorized to update")
        return redirect('employees')
    else:
        messages.error(request,"Not authorized to update")
        return redirect('employees')

@login_required
def employee_create(request):
    if request.user.is_authenticated and request.user.role in ['ADMIN','HR']:
        form = EmployeeForm()
        if request.method == 'POST':
            form=EmployeeForm(request.POST,request.FILES)
            if form.is_valid():
                emp=form.cleaned_data['empId']
                try:
                    if employee_detail.objects.filter(empId=emp).exists():
                        print("Employee ID already exists")
                        messages.error(request,"Employee ID already exists")
                        form.add_error('empId', 'This employee ID already exists.')
                        return redirect('employees')
                    else:
                        form.save()
                        print("Form saved successfully")
                        messages.success(request,"Successfully registered an Employee")
                        return redirect('employees')
                except Exception as e:
                    traceback.print_exc()
                    return render(request, './components/employee_create.html', {'form': form})
        else:
            return render(request, './components/employee_create.html',{'form': form})
    else:
        messages.error(request,"Not enough privileges to create")
        return redirect('employees')

#department modules
@login_required
def departments(request):
    objs=department.objects.all()
    return render(request, './components/departments.html',{'objs':objs,'user': request.user})

@login_required
@login_required
def delete_department(request, pk):
    if request.user.is_authenticated and request.user.role in ['ADMIN', 'HR']:
        try:
            delete_department = department.objects.get(departmentName=pk)
        except department.DoesNotExist:
            messages.error(request, "Department does not exist.")
            return redirect('department')

        if request.method == 'POST':
            try:
                delete_department.delete()
                messages.success(request, "Department deleted successfully.")
                return redirect('departments')
            except Exception as e:
                messages.error(request, f"Error deleting department: {e}")
                return redirect('departments')
        else:
            delete_department = department.objects.get(departmentName=pk)
            return render(request, "./components/delete_department.html", {'department': delete_department})
    else:
        messages.error(request, "Error")
        return redirect('departments')
    
@login_required
def department_create(request):
    if request.user.is_authenticated and request.user.role in ['ADMIN','HR']:
        form = DepartmentForm()
        if request.method == 'POST':
            form=DepartmentForm(request.POST)
            if form.is_valid():
                dept=form.cleaned_data['departmentName']
                try:
                    if department.objects.filter(departmentName=dept).exists():
                        print("Department already exists")
                        messages.error(request,"Department already exists")
                        form.add_error('departmentName', 'This department already exists.')
                    else:
                        form.save()
                        print("Form saved successfully")
                        messages.success(request,"Successfully created department")
                        return redirect('departments')
                except Exception as e:
                    traceback.print_exc()
        else:
            return render(request, './components/department_create.html',{'form': form})
    else:
        messages.error(request,"Not enough privileges to create department")
        return redirect('departments')

@login_required
def users(request):
    objs=CustomUser.objects.all()
    return render(request, './components/users.html',{'objs':objs})

@login_required
def user_create(request):
    if request.user.is_authenticated and request.user.role in ['ADMIN','HR']:
        form=UserForm()
        if request.method == 'POST':
            form=UserForm(request.POST)
            if form.is_valid():
                username=form.cleaned_data['username']
                if CustomUser.objects.filter(username=username).exists():
                    form.add_error('username', 'This username already exists.')
                else:
                    messages.success(request,'User was successfully created.')
                    form.save()
                return redirect('users')       
        return render(request, './components/user_create.html',{'form':form})
    else:
        messages.error(request,"Not authorized to create")
        return redirect('employees')


    
@login_required
def update_department(request,pk):
    if request.user.is_authenticated and request.user.role in ['ADMIN','HR']:
        update_department=department.objects.get(departmentName=pk)
        if request.method=="POST":
            form = DepartmentForm(request.POST, instance=update_department)
            if form.is_valid():
                form.save()
                messages.success(request,"Department Updated")
                return redirect('departments')
        else:
            form = DepartmentForm(instance=update_department)
        return render(request,"./components/update_department.html",{'form':form})
    else:
        messages.error(request,"Error")
        return redirect('employees')

#leave modules
@login_required
def leaves(request):
    today= date.today()
    status = request.GET.get('status', 'pending')  # Default value is 'pending'
    if status in ['approved', 'rejected'] :
        objs = Leave.objects.filter(status=status,end_date__gte=today)
    elif status == 'archived':
        status='archived'
        objs = Leave.objects.filter(end_date__lt=today)
    elif status== 'pending':
        objs=Leave.objects.filter(status=status)
    else:
        objs = Leave.objects.all()
    return render(request, './components/leaves.html',{'objs':objs,'status':status})

@login_required
def leave_apply(request):
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.empId = request.user.employee_detail
            leave.save()
            messages.success(request, "Successfully applied for leave")
            return redirect('leaves')
            # Redirect to a success page or do further processing
        else:
            # Display the form with validation errors
            messages.error(request, "There was an error in the form")
            # You can also print the form errors to the console for debugging
            print(form.errors)
    else:
        form = LeaveApplicationForm()
    return render(request, './components/leave_apply.html',{'form':form})

@login_required   
def leave_approval(request,pk):
    if request.user.is_authenticated and request.user.role in ['ADMIN','HR']:
        leave_instance=Leave.objects.get(leave_id=pk)
        if request.method=="POST":
            form = LeaveApprovalForm(request.POST, instance=leave_instance)
            if form.is_valid():
                form.save()
                status = form.cleaned_data['status']
                messages.success(request,"Done")
                if status == 'approved':
                    return redirect(reverse('leaves') + '?status=approved')
                elif status == 'rejected':
                    return redirect(reverse('leaves') + '?status=rejected')
                else:
                    return redirect(reverse('leaves') + '?status=pending')
        else:
            form = LeaveApprovalForm(instance=leave_instance)
        return render(request,"./components/leave_approval.html",{'form':form, 'leave_instance':leave_instance})
    else:
        messages.error(request,"Error")
        return redirect('leaves')
    
@login_required
def attendance(request):
    if request.GET.get('status') == 'personal':
        objs = Attendance.objects.filter(user=request.user)
        status='personal'
        return render(request,"./components/attendance.html",{'objs':objs,'status':status})
    else:
        objs=Attendance.objects.all()
        return render(request,"./components/attendance.html",{'objs':objs,'user':request.user})

@login_required
def attendanceForm(request):
    user = request.user
    if request.method == 'POST':
        time_in = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        date=request.POST.get('date')
        date=request.POST.get('date')
        check = Attendance.objects.filter(user=user,date=date).first()
        if check is not None:
            messages.error(request,"Already clocked in and clocked out")
            return redirect('attendance')
        else:
            attendance =Attendance(user=user,date=date,time_in=time_in,time_out=time_out)
            attendance.save()
        return redirect("attendance")
            
    else:
        form=AttendanceForm()
        return render(request,"./components/attendanceForm.html",{'form':form})
    
def delete_attendance(request,pk):
    if request.user.is_authenticated:
        try:
            delete_attendance = Attendance.objects.get(id=pk)
        except Attendance.DoesNotExist:
            return redirect('attendance')
        user=delete_attendance.user
        if request.method == 'POST':
            if user==request.user or request.user.role in ['ADMIN', 'HR']:
                try:
                    delete_attendance.delete()
                    messages.success(request, "Attendance deleted successfully.")
                    return redirect('attendance')
                except Exception as e:
                    messages.error(request, f"Error deleting attendance: {e}")
                    return redirect('attendance')
            else:
                messages.error(request, f"Not enough privileges")
                return redirect('attendance')
        else:
            delete_attendance = get_object_or_404(Attendance, id=pk)
            return render(request, "./components/delete_attendance.html", {'attendance': delete_attendance})
    else:
        messages.error(request, "Error")
        return redirect('attendance')
        
        
    
    

