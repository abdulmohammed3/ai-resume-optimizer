"""Supabase database client and utilities."""
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from supabase import create_client, Client
from ..config import get_settings
from ..models.resume import Resume, ResumeCreate, ResumeAnalysis
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Handle database operations with Supabase."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Client = create_client(
            self.settings.SUPABASE_URL,
            self.settings.SUPABASE_KEY
        )
    
    async def create_resume(self, resume: ResumeCreate, file_url: str) -> Resume:
        """
        Create a new resume record.
        
        Args:
            resume: Resume creation model
            file_url: URL of uploaded file
            
        Returns:
            Created Resume object
        """
        try:
            data = {
                **resume.model_dump(),
                'file_url': file_url,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('resumes').insert(data).execute()
            
            return Resume(**result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to create resume: {str(e)}")
            raise
    
    async def get_resume(self, resume_id: UUID, user_id: str) -> Optional[Resume]:
        """
        Retrieve a resume by ID.
        
        Args:
            resume_id: Resume UUID
            user_id: User ID for authorization
            
        Returns:
            Resume object if found, None otherwise
        """
        try:
            result = self.client.table('resumes')\
                .select('*')\
                .eq('id', str(resume_id))\
                .eq('user_id', user_id)\
                .execute()
                
            return Resume(**result.data[0]) if result.data else None
            
        except Exception as e:
            logger.error(f"Failed to retrieve resume: {str(e)}")
            raise
    
    async def update_resume(
        self,
        resume_id: UUID,
        user_id: str,
        updates: Dict,
        analysis: Optional[ResumeAnalysis] = None
    ) -> Resume:
        """
        Update a resume record.
        
        Args:
            resume_id: Resume UUID
            user_id: User ID for authorization
            updates: Dictionary of fields to update
            analysis: Optional new analysis results
            
        Returns:
            Updated Resume object
        """
        try:
            data = {
                **updates,
                'updated_at': datetime.utcnow().isoformat(),
            }
            
            if analysis:
                data['analysis'] = analysis.model_dump()
            
            result = self.client.table('resumes')\
                .update(data)\
                .eq('id', str(resume_id))\
                .eq('user_id', user_id)\
                .execute()
                
            return Resume(**result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to update resume: {str(e)}")
            raise
    
    async def delete_resume(self, resume_id: UUID, user_id: str):
        """
        Delete a resume record.
        
        Args:
            resume_id: Resume UUID
            user_id: User ID for authorization
        """
        try:
            self.client.table('resumes')\
                .delete()\
                .eq('id', str(resume_id))\
                .eq('user_id', user_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Failed to delete resume: {str(e)}")
            raise
    
    async def list_user_resumes(self, user_id: str) -> List[Resume]:
        """
        List all resumes for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Resume objects
        """
        try:
            result = self.client.table('resumes')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .execute()
                
            return [Resume(**row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to list resumes: {str(e)}")
            raise
    
    async def get_user_resume_count(self, user_id: str) -> int:
        """
        Get total number of resumes for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of resumes
        """
        try:
            result = self.client.table('resumes')\
                .select('id', count='exact')\
                .eq('user_id', user_id)\
                .execute()
                
            return result.count
            
        except Exception as e:
            logger.error(f"Failed to count resumes: {str(e)}")
            return 0

# Initialize database service
db = DatabaseService()