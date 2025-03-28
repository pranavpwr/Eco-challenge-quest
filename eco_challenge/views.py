from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Biome, EcoTask, UserProgress, TaskCompletion
from django.db.models import Sum
from django.contrib.auth import views as auth_views
from django.conf import settings
from .models_mongodb import TaskProofImageStorage
from django.http import HttpResponse, Http404
from bson.errors import InvalidId
from django.contrib.auth.forms import UserCreationForm

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
        
        # Create task completion record
        task_completion = TaskCompletion(
            user_progress=user_progress,
            task=task,
            proof_description=request.POST.get('proof_description', '')
        )
        
        # Handle image upload
        if 'proof_image' in request.FILES:
            image = request.FILES['proof_image']
            
            # Validate file type
            if image.content_type not in settings.ALLOWED_PROOF_IMAGE_TYPES:
                messages.error(request, "Invalid file type. Please upload a JPEG, PNG, or GIF image.")
                return redirect('biome_detail', biome_id=task.biome.id)
            
            # Validate file size
            if image.size > settings.MAX_PROOF_IMAGE_SIZE:
                messages.error(request, f"File too large. Maximum size is {settings.MAX_PROOF_IMAGE_SIZE/1024/1024}MB.")
                return redirect('biome_detail', biome_id=task.biome.id)
            
            # Save image to Django's media storage
            task_completion.proof_image = image
            
            # Also save to MongoDB GridFS
            try:
                mongodb_file_id = TaskProofImageStorage.save_image(
                    user_id=request.user.id,
                    task_id=task.id,
                    image_file=image
                )
                task_completion.mongodb_image_id = mongodb_file_id
            except Exception as e:
                # Log the error but continue with Django storage
                print(f"Error saving to MongoDB: {e}")
        
        task_completion.save()
        
        # Update user progress
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

@login_required
def task_completion_view(request, task_id):
    if request.method == 'POST':
        form = TaskCompletionForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the form data
            task_completion = form.save(commit=False)
            task_completion.user = request.user
            task_completion.task_id = task_id
            
            # Handle the uploaded image
            if 'proof_image' in request.FILES:
                image = request.FILES['proof_image']
                
                # Validate file type
                if image.content_type not in settings.ALLOWED_PROOF_IMAGE_TYPES:
                    messages.error(request, "Invalid file type. Please upload a JPEG, PNG, or GIF image.")
                    return render(request, 'task_completion.html', {'form': form})
                
                # Validate file size
                if image.size > settings.MAX_PROOF_IMAGE_SIZE:
                    messages.error(request, f"File too large. Maximum size is {settings.MAX_PROOF_IMAGE_SIZE/1024/1024}MB.")
                    return render(request, 'task_completion.html', {'form': form})
                
                task_completion.proof_image = image
            
            task_completion.save()
            messages.success(request, "Task completed successfully!")
            return redirect('dashboard')
    else:
        form = TaskCompletionForm()
    
    return render(request, 'task_completion.html', {'form': form})

@login_required
def get_mongodb_image(request, file_id):
    """View to serve images stored in MongoDB GridFS"""
    try:
        # Get the image from MongoDB
        grid_out = TaskProofImageStorage.get_image(file_id)
        
        # Set the content type and return the image
        response = HttpResponse(grid_out.read(), content_type=grid_out.content_type)
        return response
    except InvalidId:
        raise Http404("Invalid image ID")
    except Exception as e:
        raise Http404(f"Image not found: {str(e)}")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user progress for the new user
            UserProgress.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form}) 