from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('biome/<int:biome_id>/', views.biome_detail, name='biome_detail'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('mongodb-image/<str:file_id>/', views.get_mongodb_image, name='mongodb_image'),
] 