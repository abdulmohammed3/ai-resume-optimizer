"""Supabase storage client and utilities."""
from typing import BinaryIO, Optional
from supabase import create_client, Client
from ..config import get_settings
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class StorageService:
    """Handle file storage operations with Supabase."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Client = create_client(
            self.settings.SUPABASE_URL,
            self.settings.SUPABASE_KEY
        )
        self.bucket_name = "resumes"
    
    async def initialize(self):
        """Initialize storage bucket if it doesn't exist."""
        try:
            # Check if bucket exists, create if it doesn't
            buckets = self.client.storage.list_buckets()
            if not any(b['name'] == self.bucket_name for b in buckets):
                self.client.storage.create_bucket(
                    self.bucket_name,
                    public=False
                )
        except Exception as e:
            logger.error(f"Failed to initialize storage: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage initialization failed"
            )
    
    async def upload_file(
        self,
        file: BinaryIO,
        file_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload a file to Supabase storage.
        
        Args:
            file: File-like object to upload
            file_path: Path where file will be stored
            content_type: Optional MIME type
            
        Returns:
            URL of uploaded file
            
        Raises:
            HTTPException if upload fails
        """
        try:
            # Upload file
            result = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file,
                file_options={"content-type": content_type} if content_type else None
            )
            
            # Get public URL
            return self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File upload failed"
            )
    
    async def get_file(self, file_path: str) -> bytes:
        """
        Retrieve a file from storage.
        
        Args:
            file_path: Path to file in storage
            
        Returns:
            File contents as bytes
            
        Raises:
            HTTPException if file not found or retrieval fails
        """
        try:
            return self.client.storage.from_(self.bucket_name).download(file_path)
        except Exception as e:
            logger.error(f"Failed to retrieve file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
    
    async def delete_file(self, file_path: str):
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to file in storage
            
        Raises:
            HTTPException if deletion fails
        """
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File deletion failed"
            )
    
    async def get_user_storage_usage(self, user_id: str) -> int:
        """
        Get total storage usage for a user in bytes.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Total storage usage in bytes
        """
        try:
            files = self.client.storage.from_(self.bucket_name).list(f"user_{user_id}")
            return sum(file.get('metadata', {}).get('size', 0) for file in files)
        except Exception as e:
            logger.error(f"Failed to get storage usage: {str(e)}")
            return 0

# Initialize storage service
storage = StorageService()