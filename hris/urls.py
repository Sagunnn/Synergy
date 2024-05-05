from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('demo/', views.demo,name='demo'),
    path('employees/', views.employees,name='employees'),
    path('employees/record/<str:pk>/', views.employee_record,name='employee_record'),
    path('employees/update/<str:pk>/', views.update_record,name='update_record'),
    path('users/', views.users,name='users'),
    path('departments/', views.departments,name='departments'),
    path('departments/update/<str:pk>/', views.update_department,name='update_department'),
    path('departments/department_create', views.department_create,name='department_create'),
    path('leaves/', views.leaves,name='leaves'),
    path('leave_apply/',views.leave_apply,name='leave_apply'),
    path('leaves/leave_approval/<str:pk>/', views.leave_approval,name='leave_approval'),
    path('employees/employee_create/',views.employee_create,name='employee_create'),
    path('employees/user_create/',views.user_create,name='user_create'),
    path('profile/',views.profile,name='profile'),
    path('profile/update',views.profile_update,name='profile_update'),
]
