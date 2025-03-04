from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Biome, EcoTask, UserProgress, TaskCompletion
from django.db.models import Sum
from django.contrib.auth import views as auth_views

@login_required
def dashboard(request):
    user_progress, created = UserProgress.objects.get_or_create(user=request.user)
    biomes = Biome.objects.all().order_by('required_points')
    completed_tasks = TaskCompletion.objects.filter(user_progress=user_progress).order_by('-completed_at')
    
    # Calculate next level requirements
    next_level = user_progress.level + 1
    points_needed = (next_level * 100) - user_progress.total_points
    progress_percentage = (user_progress.total_points % 100)
    
    context = {
        'user_progress': user_progress,
        'biomes': biomes,
        'completed_tasks': completed_tasks,
        'next_level': next_level,
        'points_needed': points_needed,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'eco_challenge/dashboard.html', context)

@login_required
def biome_detail(request, biome_id):
    biome = get_object_or_404(Biome, id=biome_id)
    user_progress = UserProgress.objects.get(user=request.user)
    tasks = EcoTask.objects.filter(biome=biome)
    completed_task_ids = user_progress.completed_tasks.values_list('id', flat=True)
    
    context = {
        'biome': biome,
        'tasks': tasks,
        'completed_task_ids': completed_task_ids,
        'user_progress': user_progress,
    }
    return render(request, 'eco_challenge/biome_detail.html', context)

@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(EcoTask, id=task_id)
        user_progress = UserProgress.objects.get(user=request.user)
        
        if TaskCompletion.objects.filter(user_progress=user_progress, task=task).exists():
            messages.error(request, 'You have already completed this task!')
            return redirect('biome_detail', biome_id=task.biome.id)
        
        TaskCompletion.objects.create(
            user_progress=user_progress,
            task=task,
            proof_description=request.POST.get('proof_description', '')
        )
        
        user_progress.total_points += task.points
        new_level = (user_progress.total_points // 100) + 1
        if new_level > user_progress.level:
            user_progress.level = new_level
            messages.success(request, f'Congratulations! You reached level {new_level}!')
        
        user_progress.save()
        
        # Check for biome unlocks
        for biome in Biome.objects.filter(is_unlocked=False):
            if user_progress.total_points >= biome.required_points:
                biome.is_unlocked = True
                biome.save()
                messages.success(request, f'New biome unlocked: {biome.name}!')
        
        messages.success(request, f'Task completed! You earned {task.points} points!')
        return redirect('biome_detail', biome_id=task.biome.id)
    
    return redirect('dashboard')

@login_required
def profile(request):
    user_progress = UserProgress.objects.get(user=request.user)
    completed_tasks = TaskCompletion.objects.filter(user_progress=user_progress).order_by('-completed_at')
    
    context = {
        'user_progress': user_progress,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'eco_challenge/profile.html', context)

@login_required
def leaderboard(request):
    top_users = UserProgress.objects.all().order_by('-total_points')[:10]
    user_rank = UserProgress.objects.filter(total_points__gt=request.user.userprogress.total_points).count() + 1
    
    context = {
        'top_users': top_users,
        'user_rank': user_rank,
    }
    return render(request, 'eco_challenge/leaderboard.html', context)

class CustomLogoutView(auth_views.LogoutView):
    template_name = 'registration/logout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_progress'] = UserProgress.objects.get_or_create(
                user=self.request.user
            )[0]
        return context 