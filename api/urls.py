"""
URL routing for the Productivity Tracker REST API.
All paths are under the /api/ prefix (included in the project urls.py).
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root),
    path('tasks/', views.task_list),
    path('tasks/<int:pk>/', views.task_detail),
    path('habits/', views.habit_list),
    path('habits/<int:pk>/', views.habit_detail),
]
