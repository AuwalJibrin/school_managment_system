from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import SignupForm, UserProfileForm
from .models import Notification
urlpatterns = [
   path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),

    path('redirect-dashboard/', views.redirect_dashboard, name='redirect-dashboard'),
    path('pending-verification/', views.pending_verification, name='pending-verification'),
    path('verification-list/', views.verification_list, name='verification-list'),
    path('verify/approve/<int:pk>/', views.approve_student, name='approve-student'),
    path('verify/reject/<int:pk>/', views.reject_student, name='reject-student'),

    path('dashboard/admin/', views.admin_dashboard, name='admin-dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff-dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student-dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # User management
    path('user/delete/<int:pk>/', views.delete_user, name='delete-user'),
    path('user/toggle-status/<int:pk>/', views.toggle_user_status, name='toggle-user-status'),
    path('notification/send/', views.send_notification, name='send-notification'),
    path('notification/read/<int:pk>/', views.mark_notification_read, name='mark-notification-read'),
    path('acceptance-letter/', views.acceptance_letter, name='acceptance-letter'),

    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
