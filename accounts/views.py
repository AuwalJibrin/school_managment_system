from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from httpx import request
from school_web.models import Book
from .decorators import role_required
from .forms import SignupForm
from .tokens import email_token
from .decorators import role_required

User = get_user_model()


def verify_email(request, uidb64, token):
    return redirect('signin')


def signup_view(request):
    form = SignupForm(request.POST or None)

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
    else:
        return redirect('student-dashboard')
    
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

    context = {
        'total_students': students.count(),
        'total_books': books.count(),
        'students': students,
        'books': books,
        'roles_chart_data': roles_chart_data,
        'categories': categories,
        'books_by_category': books_by_category,
    }
    return render(request, 'accounts/dashboards/staff_dashboard.html', context)


@login_required
@role_required('student')
def student_dashboard(request):
    books = Book.objects.all()  # students can view all books

    context = {
        'books': books,
        'user': request.user,
        'total_books': books.count(),
    }
    return render(request, 'accounts/dashboards/student_dashboard.html', context)