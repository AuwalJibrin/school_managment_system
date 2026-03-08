from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'admission_number', 'class_name', 'attendance_percentage')
    search_fields = ('user__username', 'admission_number', 'class_name')
    list_filter = ('class_name',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'marked_by')
    list_filter = ('date', 'status', 'student__class_name')
    search_fields = ('student__user__username', 'student__admission_number')
