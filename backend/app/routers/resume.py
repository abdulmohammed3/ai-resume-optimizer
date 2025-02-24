from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Body
from fastapi.responses import JSONResponse
from typing import List, Optional
from ..models.resume import (
    Resume, ResumeCreate, ResumeUpdate, ResumeAnalysis,
    JobDescription, ResumeOptimizationRequest
)
from ..services.resume_optimizer import ResumeOptimizer
from ..dependencies import get_current_user, require_premium
from ..core.storage import storage
from ..core.database import db
from uuid import UUID, uuid4
import json
import logging

router = APIRouter()
optimizer = ResumeOptimizer()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=Resume)
async def upload_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload and analyze a resume file."""
    try:
        # Validate file type
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ['pdf', 'docx']:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are supported"
            )
        
        # Check storage quota
        usage = await storage.get_user_storage_usage(current_user["user_id"])
        if usage >= 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(
                status_code=400,
                detail="Storage quota exceeded"
            )
        
        # Generate unique file path
        file_id = str(uuid4())
        file_path = f"user_{current_user['user_id']}/{file_id}.{file_ext}"
        
        # Upload file to storage
        content = await file.read()
        file_url = await storage.upload_file(
            content,
            file_path,
            file.content_type
        )
        
        # Extract and analyze text
        text_content = await optimizer.extract_text_from_resume(
            content,
            file_ext
        )
        
        # Parse job description if provided
        job_info = None
        if job_description:
            try:
                job_data = json.loads(job_description)
                job_info = JobDescription(**job_data)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid job description format"
                )
        
        # Analyze resume
        analysis = await optimizer.analyze_resume(
            text_content,
            str(job_info) if job_info else None
        )
        
        # Create resume record
        resume = ResumeCreate(
            title=file.filename,
            content=text_content,
            file_type=file_ext,
            user_id=current_user["user_id"]
        )
        
        # Save to database
        complete_resume = await db.create_resume(resume, file_url)
        
        # Update with analysis
        return await db.update_resume(
            complete_resume.id,
            current_user["user_id"],
            {"analysis": analysis.model_dump()}
        )
        
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(e)}"
        )

@router.get("", response_model=List[Resume])
async def list_resumes(current_user: dict = Depends(get_current_user)):
    """List all resumes for the current user."""
    return await db.list_user_resumes(current_user["user_id"])

@router.get("/{resume_id}", response_model=Resume)
async def get_resume(
    resume_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve a specific resume and its analysis."""
    resume = await db.get_resume(resume_id, current_user["user_id"])
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )
    return resume

@router.put("/{resume_id}", response_model=Resume)
async def update_resume(
    resume_id: UUID,
    resume_update: ResumeUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a resume's content and trigger re-analysis."""
    # Verify resume exists and belongs to user
    existing = await db.get_resume(resume_id, current_user["user_id"])
    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )
    
    try:
        # Update resume
        updates = resume_update.model_dump(exclude_unset=True)
        if updates.get('content'):
            # Re-analyze if content changed
            analysis = await optimizer.analyze_resume(updates['content'])
            return await db.update_resume(
                resume_id,
                current_user["user_id"],
                updates,
                analysis
            )
        else:
            return await db.update_resume(
                resume_id,
                current_user["user_id"],
                updates
            )
            
    except Exception as e:
        logger.error(f"Error updating resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update resume: {str(e)}"
        )

@router.post("/{resume_id}/optimize", response_model=Resume)
async def optimize_resume(
    resume_id: UUID,
    request: ResumeOptimizationRequest,
    current_user: dict = Depends(require_premium)
):
    """Premium feature: Optimize resume for a specific job."""
    # Verify resume exists and belongs to user
    resume = await db.get_resume(resume_id, current_user["user_id"])
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )
    
    try:
        # Analyze resume against job description
        analysis = await optimizer.analyze_resume(
            resume.content,
            str(request.job_description) if request.job_description else None
        )
        
        # Generate optimized content
        sections = optimizer.classify_sections(resume.content)
        optimized = await optimizer.generate_optimized_resume(
            sections,
            request.job_description.title if request.job_description else None
        )
        
        # Update resume with optimized content and analysis
        return await db.update_resume(
            resume_id,
            current_user["user_id"],
            {"content": optimized, "optimized_content": optimized},
            analysis
        )
        
    except Exception as e:
        logger.error(f"Error optimizing resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize resume: {str(e)}"
        )

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Delete a resume and its associated file."""
    # Verify resume exists and belongs to user
    resume = await db.get_resume(resume_id, current_user["user_id"])
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )
    
    try:
        # Delete from storage first
        file_path = f"user_{current_user['user_id']}/{resume_id}"
        await storage.delete_file(file_path)
        
        # Then delete from database
        await db.delete_resume(resume_id, current_user["user_id"])
        
        return JSONResponse(
            status_code=200,
            content={"message": "Resume deleted successfully"}
        )
        
    except Exception as e:
        logger.error(f"Error deleting resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete resume: {str(e)}"
        )