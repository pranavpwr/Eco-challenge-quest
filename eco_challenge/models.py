from django.db import models
from django.contrib.auth.models import User

class Biome(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=50)
    required_points = models.IntegerField(default=0)
    image = models.ImageField(upload_to='biomes/', null=True, blank=True)
    is_unlocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class EcoTask(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    points = models.IntegerField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    biome = models.ForeignKey(Biome, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    total_points = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    completed_tasks = models.ManyToManyField(EcoTask, through='TaskCompletion')
    unlocked_biomes = models.ManyToManyField(Biome)

    def __str__(self):
        return f"{self.user.username}'s Progress"

class TaskCompletion(models.Model):
    user_progress = models.ForeignKey(UserProgress, on_delete=models.CASCADE)
    task = models.ForeignKey(EcoTask, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    proof_description = models.TextField(blank=True)
    proof_image = models.ImageField(upload_to='task_proofs/', null=True, blank=True)
    mongodb_image_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('user_progress', 'task') 