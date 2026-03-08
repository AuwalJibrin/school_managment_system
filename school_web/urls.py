
from django.urls import path
from school_web import views

urlpatterns = [
    path('', views.index, name="index"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name='contact'),
    path('e-library/', views.e_library, name='e_library'),
    path('download/<int:book_id>/', views.download_book, name='download_book'),
    path('services/', views.service, name='services'),
    
    # Book management
    path('books/', views.book_list, name='book-list'),
    path('book/add/', views.add_book, name='add-book'),
    path('book/edit/<int:pk>/', views.edit_book, name='edit-book'),
    path('book/delete/<int:pk>/', views.delete_book, name='delete-book'),
]