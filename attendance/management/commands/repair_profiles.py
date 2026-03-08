from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from attendance.models import Student

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates missing Student profiles for existing users with role=student'

    def handle(self, *args, **kwargs):
        students = User.objects.filter(role='student')
        count = 0
        for user in students:
            if not hasattr(user, 'student_profile'):
                Student.objects.create(
                    user=user,
                    admission_number=f"STUD-{user.id:04d}",
                    class_name='Default'
                )
                self.stdout.write(self.style.SUCCESS(f'Created profile for {user.username}'))
                count += 1
            else:
                self.stdout.write(f'Profile already exists for {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} missing student profiles.'))
