from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def save(self, *args, **kwargs):
        if self.role == 'admin':
            self.is_staff = True
        elif self.role == 'staff':
            self.is_staff = True
        super().save(*args, **kwargs)


# Create your models here.
