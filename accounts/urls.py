from django.urls import path
from . import views
urlpatterns = [
   path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),

    path('redirect/', views.redirect_dashboard, name='redirect-dashboard'),

    path('dashboard/admin/', views.admin_dashboard, name='admin-dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff-dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student-dashboard'),
]
