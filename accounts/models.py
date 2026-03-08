from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_email_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    academic_document = models.FileField(upload_to='academic_docs/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.role == 'admin':
            self.is_staff = True
        elif self.role == 'staff':
            self.is_staff = True
        super().save(*args, **kwargs)



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', help_text="Recipient")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}..."
