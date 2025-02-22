from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from docx import Document
from transformers import pipeline
from huggingface_hub import login
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Hugging Face pipelines
print("Initializing AI pipelines...")
try:
    # Authenticate with HuggingFace Hub
    if os.getenv("HF_TOKEN"):
        login(token=os.getenv("HF_TOKEN"))
    else:
        print("Warning: No HF_TOKEN found in environment variables")
    
    # Section classifier pipeline
    section_classifier = pipeline(
        "text-classification",
        model="has-abi/extended_distilBERT-finetuned-resumes-sections",
        token=os.getenv("HF_TOKEN")
    )
    
    # Resume optimization pipeline
    resume_optimizer = pipeline(
        "text2text-generation",
        model="nakamoto-yama/t5-resume-generation",
        token=os.getenv("HF_TOKEN")
    )
    
    print("AI pipelines initialized successfully!")
except Exception as e:
    print(f"Error initializing pipelines: {str(e)}")
    section_classifier = None
    resume_optimizer = None

def extract_text_from_docx(file):
    """Extract text content from a DOCX file."""
    doc = Document(file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def classify_resume_sections(resume_text):
    """Classify resume sections using AI pipeline."""
    if not section_classifier:
        raise Exception("Section classifier not initialized")
    
    # Split text into paragraphs
    paragraphs = [p.strip() for p in resume_text.split("\n") if p.strip()]
    
    # Classify each paragraph
    classifications = section_classifier(paragraphs)
    
    # Group paragraphs by section
    sections = {}
    for para, classification in zip(paragraphs, classifications):
        section = classification["label"]
        if section not in sections:
            sections[section] = []
        sections[section].append(para)
    
    return sections

def optimize_resume(resume_text, job_description):
    """Optimize resume using AI pipeline."""
    if not resume_optimizer:
        raise Exception("Resume optimizer not initialized")
    
    # Classify sections
    sections = classify_resume_sections(resume_text)
    
    optimized_sections = {}
    for section_name, section_text in sections.items():
        # Prepare optimization prompt
        prompt = f"""
        Job Description:
        {job_description}
        
        Resume Section ({section_name}):
        {section_text}
        
        Task: Optimize this resume section to better match the job description.
        Maintain a professional tone and highlight relevant experiences.
        """
        
        # Generate optimized section
        result = resume_optimizer(prompt, max_length=512, num_beams=5)
        optimized_sections[section_name] = result[0]["generated_text"]
    
    # Reassemble optimized sections
    return "\n\n".join(
        f"{section}\n{content}"
        for section, content in optimized_sections.items()
    )

@app.route("/")
def index():
    return jsonify({
        "message": "AI Resume Optimizer API",
        "status": "running",
        "pipelines_loaded": all([
            section_classifier,
            resume_optimizer
        ])
    })

@app.route("/optimize-resume", methods=["POST"])
def optimize_resume_endpoint():
    try:
        if not all([section_classifier, resume_optimizer]):
            return jsonify({"error": "AI pipelines not initialized"}), 500

        # Check if resume file was uploaded
        if "resume" not in request.files:
            return jsonify({"error": "No resume file uploaded"}), 400
        
        file = request.files["resume"]
        job_description = request.form.get("job_description", "")
        
        if not file or not job_description:
            return jsonify({"error": "Missing resume file or job description"}), 400
            
        # Extract text from resume
        resume_text = extract_text_from_docx(file)
        
        # Optimize resume using AI
        optimized_resume = optimize_resume(resume_text, job_description)
        
        return jsonify({
            "optimized_resume": optimized_resume
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Failed to process resume"}), 500

if __name__ == "__main__":
    app.run(debug=True)