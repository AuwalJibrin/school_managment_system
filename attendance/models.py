from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=50, unique=True)
    class_name = models.CharField(max_length=100)
    semester = models.CharField(max_length=50, default='Semester 1')
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.admission_number}"

    @property
    def attendance_percentage(self):
        total = self.attendance_set.count()
        if total == 0:
            return 0
        present = self.attendance_set.filter(status='Present').count()
        return round((present / total) * 100, 2)

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Leave', 'Leave'),
    )

    VERIFICATION_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='attendances_marked')
    
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUS_CHOICES, default='Pending')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendances_verified')
    
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection by staff")
    leave_reason = models.TextField(blank=True, null=True, help_text="Reason for leave request by student")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'date'], name='unique_attendance_daily')
        ]

    def __str__(self):
        return f"{self.student.user.username} - {self.date} - {self.status}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'student':
        Student.objects.get_or_create(
            user=instance,
            defaults={'admission_number': f"STUD-{instance.id:04d}", 'class_name': 'Default'}
        )
