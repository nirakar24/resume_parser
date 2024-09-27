from django.shortcuts import render
from .forms import ResumeForm
import PyPDF2
import os

# Define relevant keywords based on the job description
JOB_KEYWORDS = {
    "skills": ["Python", "SQL", "TensorFlow", "PyTorch", "Hadoop", "Spark", "AWS", "GCP", "Data Preprocessing"],
    "experience": ["machine learning", "data pipelines", "data cleaning", "business analytics", "AI", "cloud platforms"],
}

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_resume_data(resume_text):
    """Extract keywords like skills and experience from the resume text."""
    extracted_skills = [skill for skill in JOB_KEYWORDS['skills'] if skill.lower() in resume_text.lower()]
    extracted_experience = [exp for exp in JOB_KEYWORDS['experience'] if exp.lower() in resume_text.lower()]
    return {"skills": extracted_skills, "experience": extracted_experience}

def is_relevant(resume_data, threshold=0.5):
    """Check if the resume is relevant to the job description by comparing matched skills/experience."""
    matched_skills = len(resume_data["skills"])
    matched_experience = len(resume_data["experience"])
    
    # Calculate relevance score
    total_criteria = len(JOB_KEYWORDS["skills"]) + len(JOB_KEYWORDS["experience"])
    matched_criteria = matched_skills + matched_experience
    relevance_score = matched_criteria / total_criteria
    
    return relevance_score >= threshold, relevance_score

def index(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Extract data from form
            job_description = form.cleaned_data['job_description']
            resume_file = request.FILES['resume']
            
            # Save the uploaded resume
            resume_path = os.path.join('media', resume_file.name)
            with open(resume_path, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)

            # Extract resume text and analyze
            resume_text = extract_text_from_pdf(resume_path)
            resume_data = extract_resume_data(resume_text)
            relevant, score = is_relevant(resume_data)
            
            # Prepare result message
            if relevant:
                result_message = f"The resume is relevant to the job description. Relevance score: {score:.2f}"
            else:
                result_message = f"The resume is not relevant to the job description. Relevance score: {score:.2f}"

            return render(request, 'parsing_app/result.html', {
                'form': form,
                'resume_data': resume_data,
                'result_message': result_message,
            })
    
    else:
        form = ResumeForm()

    return render(request, 'parsing_app/index.html', {'form': form})
