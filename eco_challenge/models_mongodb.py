from pymongo import MongoClient
from django.conf import settings
import gridfs
import datetime
import os
from bson import ObjectId

class MongoDBConnection:
    def __init__(self):
        if 'mongodb' in settings.DATABASES:
            db_settings = settings.DATABASES['mongodb']
            host = db_settings['CLIENT']['host']
            port = db_settings['CLIENT']['port']
            username = db_settings['CLIENT']['username']
            password = db_settings['CLIENT']['password']
            
            if username and password:
                self.client = MongoClient(host, port, username=username, password=password)
            else:
                self.client = MongoClient(host, port)
            
            self.db = self.client[db_settings['NAME']]
            self.fs = gridfs.GridFS(self.db, collection=settings.MONGODB_GRIDFS_COLLECTION)
        else:
            raise Exception("MongoDB configuration not found in settings")

class TaskProofImageStorage:
    @staticmethod
    def save_image(user_id, task_id, image_file, filename=None):
        """
        Save an image to MongoDB GridFS
        
        Args:
            user_id: The ID of the user who completed the task
            task_id: The ID of the completed task
            image_file: The uploaded image file object
            filename: Optional custom filename
            
        Returns:
            The ObjectId of the stored file
        """
        conn = MongoDBConnection()
        
        if not filename:
            filename = image_file.name
        
        # Store metadata with the image
        metadata = {
            'user_id': user_id,
            'task_id': task_id,
            'upload_date': datetime.datetime.now(),
            'content_type': image_file.content_type,
            'filename': filename
        }
        
        # Store the file in GridFS
        file_id = conn.fs.put(
            image_file.read(),
            filename=filename,
            content_type=image_file.content_type,
            metadata=metadata
        )
        
        return str(file_id)
    
    @staticmethod
    def get_image(file_id):
        """
        Retrieve an image from MongoDB GridFS
        
        Args:
            file_id: The ObjectId of the stored file
            
        Returns:
            The GridOut object representing the file
        """
        conn = MongoDBConnection()
        return conn.fs.get(ObjectId(file_id))
    
    @staticmethod
    def get_user_images(user_id):
        """
        Get all images uploaded by a specific user
        
        Args:
            user_id: The ID of the user
            
        Returns:
            A list of GridOut objects
        """
        conn = MongoDBConnection()
        return list(conn.fs.find({"metadata.user_id": user_id}))
    
    @staticmethod
    def get_task_images(task_id):
        """
        Get all images uploaded for a specific task
        
        Args:
            task_id: The ID of the task
            
        Returns:
            A list of GridOut objects
        """
        conn = MongoDBConnection()
        return list(conn.fs.find({"metadata.task_id": task_id})) 