"""Resume section templates for AI-powered optimization."""

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

RESUME_PROMPT_TEMPLATE = """Create a polished, professional resume for a {job_title} position using the following information:

Contact Information:
{contact}

Professional Experience:
{experience}

Education:
{education}

Skills:
{skills}

Projects:
{projects}

Awards:
{awards}

Format the resume with clear section headings and consistent formatting. Use bullet points for achievements and responsibilities. Keep the language professional and concise."""