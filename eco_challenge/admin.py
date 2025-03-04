from django.contrib import admin
from .models import Biome, EcoTask, UserProgress, TaskCompletion

@admin.register(Biome)
class BiomeAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_points', 'is_unlocked')
    list_filter = ('is_unlocked',)
    search_fields = ('name', 'description')

@admin.register(EcoTask)
class EcoTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'biome', 'points', 'difficulty')
    list_filter = ('biome', 'difficulty')
    search_fields = ('title', 'description')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'level')
    search_fields = ('user__username',)

@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('user_progress', 'task', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('user_progress__user__username', 'task__title') 