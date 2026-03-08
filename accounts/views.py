from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.utils import timezone
from school_web.models import Book
from .decorators import role_required
from .forms import SignupForm, UserProfileForm, SendNotificationForm
from .models import Notification
from .tokens import email_token
from results.models import Result

User = get_user_model()

@login_required
def send_notification(request):
    if request.user.role not in ['admin', 'staff']:
        messages.error(request, "You don't have permission to send notifications.")
        return redirect('redirect-dashboard')
    
    if request.method == 'POST':
        form = SendNotificationForm(request.POST)
        if form.is_valid():
            target = form.cleaned_data.get('target_group')
            message_text = form.cleaned_data.get('message')
            
            if target != 'specific':
                if target == 'students':
                    recipients = User.objects.filter(role='student')
                elif target == 'staff':
                    recipients = User.objects.filter(role='staff')
                else:  # 'all'
                    recipients = User.objects.filter(role__in=['student', 'staff'])
                
                # Bulk create notifications
                notifications = [
                    Notification(user=recipient, message=message_text, sender=request.user)
                    for recipient in recipients
                ]
                Notification.objects.bulk_create(notifications)
                messages.success(request, f"Broadcast sent to all {recipients.count()} {target}!")
            else:
                notification = form.save(commit=False)
                notification.sender = request.user
                notification.save()
                messages.success(request, f"Notification sent to {notification.user.username}!")
            
            return redirect('redirect-dashboard')
    else:
        # Pre-fill recipient if passed in GET
        recipient_id = request.GET.get('recipient')
        initial = {}
        if recipient_id:
            initial['user'] = recipient_id
        form = SendNotificationForm(initial=initial)
    
    return render(request, 'accounts/send_notification.html', {'form': form})

def verify_email(request, uidb64, token):
    return redirect('signin')


def signup_view(request):
    form = SignupForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        user = form.save(commit=False)

        # SIMPLE MODE: activate immediately
        user.is_active = True
        user.is_email_verified = True
        user.save()

        messages.success(request, 'Account created successfully. Please sign in.')
        return redirect('signin')

    return render(request, 'accounts/signup.html', {'form': form})


def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')


        user = authenticate(request, username=username, password=password)
       
        if user is not None:
            if user.is_active:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                return redirect('redirect-dashboard')
            else:
                messages.error(request, 'Account is disabled.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/signin.html')


def logout_view(request):
    """Logout user and redirect to signin"""
    logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('signin')


@login_required
def redirect_dashboard(request):
    if request.user.role == 'admin':
        return redirect('admin-dashboard')
    elif request.user.role == 'staff':
        return redirect('staff-dashboard')
    else:  # student
        if not request.user.is_verified:
            return redirect('pending-verification')
        return redirect('student-dashboard')

@login_required
def pending_verification(request):
    if request.user.is_verified:
        return redirect('redirect-dashboard')
        
    if request.method == 'POST' and request.user.role == 'student':
        from .forms import StudentDocumentForm
        form = StudentDocumentForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Reset rejection reason when student re-uploads
            user = form.save(commit=False)
            user.rejection_reason = ""
            user.save()
            messages.success(request, "Document updated successfully. Awaiting new review.")
            return redirect('pending-verification')
            
    return render(request, 'accounts/pending_verification.html')
    
@login_required
@role_required('admin')
def admin_dashboard(request):
    users = User.objects.all()
    books = Book.objects.all()

    roles_chart_data = {
        'labels': ['Students', 'Staff', 'Admins'],
        'counts': [
            users.filter(role='student').count(),
            users.filter(role='staff').count(),
            users.filter(role='admin').count()
        ]
    }

    categories = books.values_list('category', flat=True).distinct()
    books_by_category = [books.filter(category=cat).count() for cat in categories]

    context = {
        'total_users': users.count(),
        'total_students': users.filter(role='student').count(),
        'total_staff': users.filter(role='staff').count(),
        'total_books': books.count(),
        'total_results': Result.objects.count(),
        'users': users,
        'books': books,
        'roles_chart_data': roles_chart_data,
        'categories': categories,
        'books_by_category': books_by_category,
    }
    return render(request, 'accounts/dashboards/admin_dashboard.html', context)


@login_required
@role_required('staff')
def staff_dashboard(request):
    students = User.objects.filter(role='student')
    books = Book.objects.filter(assigned_to=request.user)

    roles_chart_data = {
        'labels': ['Students'],
        'counts': [students.count()]
    }

    categories = books.values_list('category', flat=True).distinct()
    books_by_category = [books.filter(category=cat).count() for cat in categories]
    
    # Attendance Verification
    # Attendance Verification
    from attendance.models import Attendance
    pending_attendance_count = Attendance.objects.filter(verification_status='Pending').count()

    context = {
        'total_students': students.count(),
        'total_books': books.count(),
        'students': students,
        'books': books,
        'roles_chart_data': roles_chart_data,
        'categories': categories,
        'books_by_category': books_by_category,
        'notices': request.user.notifications.all()[:5],
        'pending_attendance_count': pending_attendance_count,
        'total_results': Result.objects.count(),
    }
    return render(request, 'accounts/dashboards/staff_dashboard.html', context)


@login_required
@role_required('student')
def student_dashboard(request):
    books = Book.objects.all()  # students can view all books
    notifications = request.user.notifications.all()[:5]  # Get latest 5 notices

    context = {
        'books': books,
        'user': request.user,
        'total_books': books.count(),
        'notices': notifications,
        'recent_results': Result.objects.filter(student__user=request.user).order_by('-created_at')[:5],
    }
    return render(request, 'accounts/dashboards/student_dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'redirect-dashboard'))


@login_required
@role_required('admin')
def delete_user(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_to_delete.delete()
        messages.success(request, f"User {user_to_delete.username} deleted successfully.")
        return redirect('admin-dashboard')
    return render(request, 'accounts/user_confirm_delete.html', {'user_to_delete': user_to_delete})


@login_required
@role_required('admin')
def toggle_user_status(request, pk):
    user_to_toggle = get_object_or_404(User, pk=pk)
    user_to_toggle.is_active = not user_to_toggle.is_active
    user_to_toggle.save()
    status = "activated" if user_to_toggle.is_active else "deactivated"
    messages.success(request, f"User {user_to_toggle.username} has been {status}.")
    return redirect('admin-dashboard')

@login_required
@role_required('admin')
def verification_list(request):
    unverified_students = User.objects.filter(role='student', is_verified=False)
    verified_students = User.objects.filter(role='student', is_verified=True).order_by('-id')[:10]
    return render(request, 'accounts/verification_list.html', {
        'unverified_students': unverified_students,
        'verified_students': verified_students,
    })

@login_required
@role_required('admin')
def approve_student(request, pk):
    student = get_object_or_404(User, pk=pk, role='student')
    student.is_verified = True
    student.rejection_reason = ""
    student.save()
    
    # Notify the student
    Notification.objects.create(
        user=student,
        sender=request.user,
        message="Your account has been verified! You now have full access to the dashboard."
    )
    
    messages.success(request, f"Student {student.username} approved.")
    return redirect('verification-list')

@login_required
@role_required('student')
def acceptance_letter(request):
    if not request.user.is_verified:
        messages.warning(request, "Your account must be verified before you can access the acceptance letter.")
        return redirect('pending-verification')
        
    context = {
        'today': timezone.now(),
        'user': request.user,
    }
    return render(request, 'accounts/acceptance_letter.html', context)

@login_required
@role_required('admin')
def reject_student(request, pk):
    if request.method == 'POST':
        student = get_object_or_404(User, pk=pk, role='student')
        reason = request.POST.get('reason')
        student.is_verified = False
        student.rejection_reason = reason
        student.save()
        
        # Notify the student
        Notification.objects.create(
            user=student,
            sender=request.user,
            message=f"Your verification was rejected. Reason: {reason}"
        )
        
        messages.warning(request, f"Student {student.username} rejected.")
    return redirect('verification-list')