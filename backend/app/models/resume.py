from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

class JobDescription(BaseModel):
    """Job description model."""
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Full job description")
    company: Optional[str] = Field(None, description="Company name")
    requirements: Optional[List[str]] = Field(None, description="Job requirements")

class ResumeBase(BaseModel):
    """Base resume model with shared attributes."""
    title: str = Field(..., description="Resume title or job position")
    content: str = Field(..., description="Raw resume text content")
    file_type: str = Field(..., description="Original file type (e.g., 'pdf', 'docx')")

class ResumeCreate(ResumeBase):
    """Resume creation model."""
    user_id: str = Field(..., description="ID of the user who owns this resume")

class ResumeUpdate(BaseModel):
    """Resume update model with optional fields."""
    title: Optional[str] = None
    content: Optional[str] = None
    file_type: Optional[str] = None

class ResumeOptimizationRequest(BaseModel):
    """Request model for resume optimization."""
    resume_id: UUID = Field(..., description="ID of the resume to optimize")
    job_description: Optional[JobDescription] = Field(None, description="Target job description")
    optimization_level: str = Field(
        "standard",
        description="Level of optimization (standard, advanced, professional)"
    )

class ResumeAnalysis(BaseModel):
    """Resume analysis results."""
    score: float = Field(..., description="Overall resume score", ge=0, le=100)
    feedback: List[Dict[str, str]] = Field(..., description="List of feedback items")
    suggestions: List[str] = Field(..., description="Improvement suggestions")
    keywords_found: List[str] = Field(..., description="Relevant keywords found")
    missing_keywords: List[str] = Field(..., description="Suggested missing keywords")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

class Resume(ResumeBase):
    """Complete resume model including database fields."""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    analysis: Optional[ResumeAnalysis] = None
    optimized_content: Optional[str] = Field(None, description="Optimized resume content")
    original_filename: Optional[str] = None
    file_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True