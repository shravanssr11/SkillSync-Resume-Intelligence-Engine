🚀 SkillSync: Resume Intelligence Engine

SkillSync is an AI-powered application that helps job seekers align their resumes with job descriptions by identifying missing skills and ATS (Applicant Tracking System) keywords. It leverages LangChain,LangGraph, Groq LLMs, and Streamlit to provide instant, actionable feedback for resume optimization.


✨ Features

📂 Resume Upload: Upload your resume in PDF format.

📝 Job Description Input: Paste the target job description.

🎯 Missing Skills Detection: Highlights essential skills missing from your resume.

🧩 Recommended ATS Keywords: Extracts ATS-friendly keywords to improve your resume ranking.

📝 Final Feedback: Generates personalized optimization suggestions from an AI career counselor.

🔄 Smart Matching Rules:

Recognizes synonyms (e.g., ML = Machine Learning).

Maps general skills to specific tools (e.g., Machine Learning → TensorFlow, PyTorch).

Identifies abbreviations and full forms (e.g., React.js = React).

🛠️ Tech Stack

Streamlit
 – Interactive UI for resume and job description input.

LangChain
 – Workflow orchestration.

Groq LLM (LLaMA-3.3 70B)
 – AI model for structured analysis.

PyPDF2
 – Extracts text from resumes (PDF).

Pydantic
 – Defines structured outputs.

Python dotenv
 – Secure API key management.

 ⚙️ Installation

 1. **Clone the Repository**
    git clone https://github.com/shravanssr11/SkillSync-Resume-Intelligence-Engine

 2. **Create a Virtual Environment**
    python -m venv venv
    source venv/bin/activate   # Mac/Linux
    venv\Scripts\activate      # Windows

 3. **Install Dependencies**
    pip install -r requirements.txt

 4. **Set up Environment Variables**
    Create a .env file in the root directory:

    GROQ_API_KEY=your_groq_api_key_here

 ▶️ Usage

 Run the app with: streamlit run app.py


 **Steps to Use**:

 1. Upload your resume PDF from the sidebar.

 2. Paste the job description into the text area.

 3. Click 🔎 Analyze.

 4. View:

🎯 Missing Skills

🧩 Recommended ATS Keywords

📝 Final Thoughts


    