from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('', views.result_list, name='result-list'),
    path('add/', views.result_add, name='result-add'),
    path('edit/<int:pk>/', views.result_edit, name='result-edit'),
    path('delete/<int:pk>/', views.result_delete, name='result-delete'),
]
