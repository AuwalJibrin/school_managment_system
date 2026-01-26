
from django.urls import path
from school_web import views

urlpatterns = [
    path('', views.index, name="index"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name='contact'),
    path('e-library/', views.e_library, name='e_library'),
    path('download/<int:book_id>/', views.download_book, name='download_book'),
  
    
   
]