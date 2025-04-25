from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 #convert MB to bytes

    def validate_uploaded_file(self, file: UploadFile):
        
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED

        return True, ResponseSignal.FILE_UPLOAD_SUCCESS.value


    def get_clean_filename(self, orignal_filename: str):
        
        # replace spaces with underscore
        cleaned_filename = orignal_filename.replace(" ", "_").lower()

        # lowercase file name and remove any special characters, except '_' and '.'
        cleaned_filename = re.sub(r"[^a-z0-9_.]", "", cleaned_filename)

        return cleaned_filename


    def generate_unique_file_path(self, orignal_filename: str, project_id: str):
        
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_filename = self.get_clean_filename(orignal_filename= orignal_filename)

        new_filename = random_key + '_' + cleaned_filename
        new_file_path = os.path.join(
            project_path,
            new_filename
            
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = random_key + '_' + cleaned_filename 
            new_filename_path = os.path.join(
                project_dir,
                random_key + '_' + cleaned_filename 
            )

        return new_file_path, new_filename
            
