from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('mark/', views.mark_attendance, name='mark-attendance'),
    path('mark/student/', views.student_mark_attendance, name='student-mark-attendance'),
    path('mark/leave/', views.student_request_leave, name='student-request-leave'),
    path('verify/', views.staff_verify_attendance, name='verify-attendance'),
    path('students/overview/', views.staff_student_list, name='staff-student-list'),
    path('admin/', views.view_attendance_admin, name='admin-attendance'),
    path('export/', views.export_attendance_csv, name='export-attendance'),
    path('export-pdf/', views.export_attendance_pdf, name='export-attendance-pdf'),
    path('defaulters/', views.defaulters_list, name='defaulters-list'),
    path('my/', views.view_attendance_student, name='student-attendance'),
    
    # Student Management
    path('students/', views.student_list, name='student-list'),
    path('students/add/', views.student_add, name='student-add'),
    path('students/edit/<int:pk>/', views.student_edit, name='student-edit'),
    path('students/delete/<int:pk>/', views.student_delete, name='student-delete'),
    path('students/view/<int:pk>/', views.student_view, name='student-view'),
]
