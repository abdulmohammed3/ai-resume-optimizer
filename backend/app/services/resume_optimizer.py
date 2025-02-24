import re
import difflib
from typing import Dict, List, Optional
from datetime import datetime
from docx import Document
from openai import AsyncOpenAI
from ..core.templates import SECTION_TEMPLATES, RESUME_PROMPT_TEMPLATE
from ..models.resume import ResumeAnalysis
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)

class ResumeOptimizer:
    """Service for resume analysis and optimization using OpenAI."""

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)

    @staticmethod
    def text_similarity(a: str, b: str) -> float:
        """Calculate text similarity using difflib."""
        return difflib.SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def validate_and_clean(text: str) -> str:
        """Validate and clean generated text."""
        # Remove repeated phrases
        text = re.sub(r'(\b\w+\b)(?:\s+\1)+', r'\1', text)
        
        # Remove special encoding artifacts
        text = text.replace('', "'")
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    @staticmethod
    async def extract_text_from_resume(file_content: bytes, file_type: str) -> str:
        """Extract text content from resume file."""
        try:
            if file_type.lower() == 'docx':
                doc = Document(file_content)
                return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise

    @staticmethod
    def classify_sections(resume_text: str) -> Dict[str, str]:
        """Classify resume sections using regex patterns."""
        sections = {}
        current_section = None
        
        for line in resume_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            section_match = re.match(
                r'^\s*(contact|experience|education|skills|projects|awards)\s*:?\s*$',
                line,
                re.IGNORECASE
            )
            if section_match:
                current_section = section_match.group(1).lower()
                sections[current_section] = []
                continue
                
            if current_section:
                sections[current_section].append(line)
                
        return {k: "\n".join(v) for k, v in sections.items()}

    async def optimize_section(
        self,
        section_name: str,
        content: str,
        job_title: str = "software engineering"
    ) -> str:
        """Optimize a resume section using structured templates."""
        try:
            prompt = SECTION_TEMPLATES[section_name].format(
                content=content,
                job_title=job_title
            )
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            optimized_text = response.choices[0].message.content
            return self.validate_and_clean(optimized_text)
            
        except Exception as e:
            logger.error(f"Error optimizing {section_name}: {str(e)}")
            return content  # Return original if optimization fails

    async def generate_optimized_resume(
        self,
        sections: Dict[str, str],
        job_title: str = "Software Engineering"
    ) -> str:
        """Generate a cohesive, optimized resume."""
        try:
            # Generate prompt using template
            prompt = RESUME_PROMPT_TEMPLATE.format(
                job_title=job_title,
                contact=sections.get('contact', ''),
                experience=sections.get('experience', ''),
                education=sections.get('education', ''),
                skills=sections.get('skills', ''),
                projects=sections.get('projects', ''),
                awards=sections.get('awards', '')
            )
            
            # Generate optimized resume using GPT-4
            response = await self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for better formatting
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2000
            )
            
            optimized_resume = self.validate_and_clean(
                response.choices[0].message.content
            )
            
            # Split into lines and remove empty lines
            formatted_lines = [
                line.strip()
                for line in optimized_resume.split('\n')
                if line.strip()
            ]
            
            return "\n".join(formatted_lines)
            
        except Exception as e:
            logger.error(f"Error generating resume: {str(e)}")
            raise

    async def analyze_resume(
        self,
        content: str,
        job_description: Optional[str] = None
    ) -> ResumeAnalysis:
        """
        Analyze resume content and provide feedback.
        
        Args:
            content: Raw resume text content
            job_description: Optional job description to match against
            
        Returns:
            ResumeAnalysis object containing scores and feedback
        """
        # Implementation from previous version
        system_prompt = """You are an expert resume analyst. Analyze the resume provided and give:
        1. A score out of 100
        2. Specific feedback on improvements
        3. Keywords found in the resume
        4. Important keywords that should be added
        Format your response as JSON."""

        user_prompt = f"Resume content:\n{content}"
        if job_description:
            user_prompt += f"\n\nJob Description:\n{job_description}"

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            analysis_dict = eval(result)
            
            return ResumeAnalysis(
                score=float(analysis_dict.get('score', 0)),
                feedback=[
                    {"category": k, "suggestion": v}
                    for k, v in analysis_dict.get('feedback', {}).items()
                ],
                suggestions=analysis_dict.get('suggestions', []),
                keywords_found=analysis_dict.get('keywords_found', []),
                missing_keywords=analysis_dict.get('missing_keywords', [])
            )
            
        except Exception as e:
            logger.error(f"Error in resume analysis: {str(e)}")
            raise