from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import department,employee_detail,CustomUser,Leave,Profile
from .forms import EmployeeForm,UserForm,DepartmentForm,LeaveApplicationForm,LeaveApprovalForm, ProfileForm
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
import traceback
from datetime import date
from django.urls import reverse


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
            info=Profile.objects.filter(empId=obj.empId)
            if obj:
                return render(request, './components/profile.html', {'obj': obj,'info': info})
            else:
                print('No matching employee_detail object for the user')
                return redirect('dashboard')
        except employee_detail.DoesNotExist:
            print('does not exist')
            return redirect('dashboard')

@login_required
def profile_update(request):
    if request.user.is_authenticated:
        update_profile = profile.objects.filter(empId=request.user.employee_detail.empId)
        if request.method == "POST":
            form = ProfileForm(request.POST, instance=update_profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully")
                return redirect('profile')
        else:
            form = ProfileForm(instance=update_profile)
        return render(request, "./components/update_profile.html", {'form': form})
    else:
        messages.error(request, "Not authorized to update")
        return redirect('profile')


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

@login_required
def dashboard(request):
    employee_count = employee_detail.objects.count()
    department_count = department.objects.count()
    today = date.today()
    leaves_count = Leave.objects.filter(start_date__lte=today, end_date__gte=today, status = 'approved').count()
    context = {
        'employee_count': employee_count,
        'department_count': department_count,
        'leaves_count': leaves_count
    }
    return render(request, './components/dashboard.html', context)
    
#employees modules
@login_required
def employees(request):
    objs=employee_detail.objects.all()
    for employee in objs:
        print(employee.lastName)
    if request.method == 'POST':
        if 'Delete' in request.POST:
            print("Delete employee")
            username=request.POST.get('Delete')
            try:
                user = CustomUser.objects.get(username=username)
                employee = employee_detail.objects.get(user=user)
                user.delete()  # Delete the associated CustomUser object
                employee.delete()  # Delete the employee_detail object
            except ObjectDoesNotExist:
                print("Function does not exist")          
    return render(request, './components/employees.html',{'objs':objs,'user':request.user})
    



@login_required
def employee_record(request,pk):
    if request.user.is_authenticated:
        employee_record=employee_detail.objects.get(empId=pk)
        return render(request,"./components/employee_record.html",{'employee_record':employee_record})

@login_required
def update_record(request,pk):
    if request.user.is_authenticated and request.user.role in ['ADMIN','HR']:
        if request.user.role == 'ADMIN' or request.user.empId ==pk:
            update_record=employee_detail.objects.get(empId=pk)
            if request.method=="POST":
                form = EmployeeForm(request.POST, request.FILES,instance=update_record)
                if form.is_valid():
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
                    else:
                        form.save()
                        print(employee_detail.profile_picture.url)
                        print("Form saved successfully")
                        messages.success(request,"Successfully registered an Employee")
                        return redirect('employees')
                except Exception as e:
                    traceback.print_exc()
        else:
            return render(request, './components/employee_create.html',{'form': form})
    else:
        messages.error(request,"Not enough privileges to create")
        return redirect('employees')

#department modules
@login_required
def departments(request):
    objs=department.objects.all()
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role not in ["ADMIN", "MANAGER"]:
            raise PermissionDenied
        if 'Delete' in request.POST:
            print("Delete Department")
            deptName=request.POST.get('Delete')
            try:
                department_obj = department.objects.get(departmentName=deptName)
                department_obj.delete()
            except ObjectDoesNotExist:
                print("Function does not exist")
    return render(request, './components/departments.html',{'objs':objs,'user': request.user})

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
    if status in ['pending', 'approved', 'rejected']:
        objs = Leave.objects.filter(status=status,end_date__lte=today)
    elif status == 'archived':
        objs = Leave.objects.filter(end_date__lt=today)
    else:
        objs = Leave.objects.all()
    return render(request, './components/leaves.html',{'objs':objs})

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

