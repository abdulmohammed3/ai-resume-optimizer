import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from docx import Document
import openai
import re
from datetime import datetime
from dateutil import parser
import os
import logging
import difflib

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Section-specific templates
SECTION_TEMPLATES = {
    "contact": """Format the following contact information:
{content}

Output format:
Full Name: [name]
Phone: [phone]
Email: [email]
Location: [location]
LinkedIn: [linkedin] (if available)
Portfolio: [portfolio] (if available)""",

    "experience": """Optimize the following work experience for a {job_title} position:
{content}

Output format:
- Company: [company]
- Position: [position]
- Dates: [start_date] - [end_date]
- Responsibilities:
  * [responsibility 1]
  * [responsibility 2]
  * [responsibility 3]""",

    "education": """Format the following education information:
{content}

Output format:
- Institution: [institution]
- Degree: [degree]
- Field of Study: [field]
- Dates: [start_date] - [end_date]
- GPA: [gpa] (if available)""",

    "skills": """Extract and format skills from:
{content}

Output format:
- Technical: [skill1], [skill2], [skill3]
- Soft: [skill1], [skill2]""",

    "projects": """Format the following projects:
{content}

Output format:
- Project: [project name]
  * Description: [1-2 sentence description]
  * Technologies: [tech1], [tech2]
  * Impact: [quantifiable impact]"""
}

def text_similarity(a, b):
    """Calculate text similarity using difflib."""
    return difflib.SequenceMatcher(None, a, b).ratio()

def validate_and_clean(text):
    """Validate and clean generated text."""
    # Remove repeated phrases
    text = re.sub(r'(\b\w+\b)(?:\s+\1)+', r'\1', text)
    
    # Remove special encoding artifacts
    text = text.replace('\u2019', "'")
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_text_from_docx(file):
    """Extract text content from a DOCX file."""
    doc = Document(file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def classify_sections(resume_text):
    """Classify resume sections using regex patterns."""
    sections = {}
    current_section = None
    
    for line in resume_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        # Match section headers with optional colon and whitespace, case-insensitive
        section_match = re.match(r'^\s*(contact|experience|education|skills|projects|awards)\s*:?\s*$', line, re.IGNORECASE)
        if section_match:
            current_section = section_match.group(1).lower()
            sections[current_section] = []
            continue
            
        if current_section:
            sections[current_section].append(line)
            
    return {k: "\n".join(v) for k, v in sections.items()}

def optimize_section(section_name, content, job_description):
    """Optimize a resume section using structured templates."""
    try:
        prompt = SECTION_TEMPLATES[section_name].format(
            content=content,
            job_title=job_description.get('title', 'software engineering')
        )
        
        response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[{"role": "user", "content": prompt}],
          temperature=0.3,
          max_tokens=1000
        )
        
        optimized_text = response.choices[0].message.content
        return validate_and_clean(optimized_text)
        
    except Exception as e:
        logger.error(f"Error optimizing {section_name}: {str(e)}")
        return content  # Return original if optimization fails

@app.route("/optimize-resume", methods=["POST"])
def optimize_resume():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No resume file uploaded"}), 400
            
        file = request.files["resume"]
        
        if not file:
            return jsonify({"error": "Missing resume file"}), 400
            
        try:
            job_description = json.loads(request.form.get("job_description", "{}"))
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid job description format"}), 400
            
        # Extract and classify resume text
        resume_text = extract_text_from_docx(file)
        sections = classify_sections(resume_text)
        
        # Generate cohesive resume prompt
        prompt = f"""Create a polished, professional resume for a {job_description.get('title', 'Software Engineering')} position using the following information:

Contact Information:
{sections.get('contact', '')}

Professional Experience:
{sections.get('experience', '')}

Education:
{sections.get('education', '')}

Skills:
{sections.get('skills', '')}

Projects:
{sections.get('projects', '')}

Awards:
{sections.get('awards', '')}

Format the resume with clear section headings and consistent formatting. Use bullet points for achievements and responsibilities. Keep the language professional and concise."""
        
        # Generate cohesive resume using gpt-4 for better formatting
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        optimized_resume = validate_and_clean(response.choices[0].message.content)
        
        # Split into lines and remove any empty lines
        formatted_lines = [line.strip() for line in optimized_resume.split('\n') if line.strip()]
        
        return jsonify({
            "optimized_resume": "\n".join(formatted_lines),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return jsonify({"error": "Failed to process resume"}), 500

if __name__ == "__main__":
    app.run(debug=True)