from django.core.management.base import BaseCommand
from eco_challenge.models import TaskCompletion
from eco_challenge.models_mongodb import TaskProofImageStorage
import os

class Command(BaseCommand):
    help = 'Migrates existing task proof images to MongoDB GridFS'

    def handle(self, *args, **kwargs):
        # Get all task completions with images
        completions = TaskCompletion.objects.filter(proof_image__isnull=False).exclude(proof_image='')
        
        self.stdout.write(f"Found {completions.count()} images to migrate")
        
        success_count = 0
        error_count = 0
        
        for completion in completions:
            try:
                # Skip if already has MongoDB ID
                if completion.mongodb_image_id:
                    self.stdout.write(f"Skipping already migrated image for task {completion.task.id}")
                    continue
                
                # Open the image file
                if not os.path.exists(completion.proof_image.path):
                    self.stdout.write(self.style.WARNING(f"Image file not found: {completion.proof_image.path}"))
                    error_count += 1
                    continue
                
                with open(completion.proof_image.path, 'rb') as f:
                    # Get content type based on file extension
                    _, ext = os.path.splitext(completion.proof_image.name)
                    content_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif'
                    }.get(ext.lower(), 'application/octet-stream')
                    
                    # Create a file-like object with content_type attribute
                    class FileWrapper:
                        def __init__(self, file, name, content_type):
                            self.file = file
                            self.name = name
                            self.content_type = content_type
                        
                        def read(self):
                            return self.file.read()
                    
                    file_wrapper = FileWrapper(
                        f, 
                        os.path.basename(completion.proof_image.name),
                        content_type
                    )
                    
                    # Save to MongoDB
                    mongodb_file_id = TaskProofImageStorage.save_image(
                        user_id=completion.user_progress.user.id,
                        task_id=completion.task.id,
                        image_file=file_wrapper
                    )
                    
                    # Update the record
                    completion.mongodb_image_id = mongodb_file_id
                    completion.save()
                    
                    success_count += 1
                    self.stdout.write(f"Migrated image for task {completion.task.id}")
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error migrating image: {str(e)}"))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Migration complete. Success: {success_count}, Errors: {error_count}")) 