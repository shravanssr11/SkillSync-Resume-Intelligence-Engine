import streamlit as st
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq
import PyPDF2
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
load_dotenv()

# -------------------- UI HEADER --------------------
st.markdown("""
# 🚀 SkillSync: Resume Intelligence Engine  
#### Your AI-powered assistant for resume–job description alignment  

Upload your **resume (PDF)** and paste the **job description** to get:  
- 🎯 Missing Skills  
- 🧩 Recommended ATS Keywords  
- 📝 Personalized Final Feedback  
""")

# -------------------- Sidebar --------------------
with st.sidebar:
    st.header("📂 Upload Your Resume")
    file = st.file_uploader("Upload PDF", type="pdf")

# -------------------- Job Description Input --------------------
jd = st.text_area(
    label=" ",
    placeholder="Paste the Job Description here...",
    height=200,
    label_visibility="collapsed"
)

# -------------------- Analyse Button --------------------
analyze_btn = st.button("🔎 Analyze")

if analyze_btn:
    if file is None:
        st.warning("⚠️ Please upload your resume (PDF) before analyzing.")
    elif jd.strip() == "":
        st.warning("⚠️ Please enter the Job Description before analyzing.")
    else:
        with st.spinner("⏳ Analysing... Please wait"):
            # ---------------- Extract Resume Text ----------------
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            #*************************define llm************************************************
            groq_api_key = os.getenv("GROQ_API_KEY")
            llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

            #*************************define state********************************************
            class State(TypedDict):
                job_description: str
                resume: str
                required_skills: list[str]
                required_keywords: list[str]
                skills: list[str]
                keywords: list[str]
                missing_skills: list[str]
                missing_keywords: list[str]
                final_missing_skills: list[str]
                final_missing_keywords: list[str]
                final_thought: str

            #************************structured_llm_for_job_description**************************************
            class schema1(BaseModel):
                skills: list[str] = Field(description="key skills mentioned in job description")
                keywords: list[str] = Field(description="ats keywords according to job description")
            structured_llm_1 = llm.with_structured_output(schema1)

            #***********************structured_llm_for_resume***********************************
            class schema2(BaseModel):
                skills: list[str] = Field(description="key skills mentioned in resume")
                keywords: list[str] = Field(description="ats keywords present in resume")
            structured_llm_2 = llm.with_structured_output(schema2)

            #***********************structured_llm_for_missing*********************************
            class schema3(BaseModel):
                skills: list[str] = Field(description="skills required by job description but missing from resume")
                keywords: list[str] = Field(description="ATS keywords required by job description but missing from resume")
            structured_llm_3 = llm.with_structured_output(schema3)

            #**********************Defining_graph_nodes*****************************************
            def jd_parser(state: State):
                response = structured_llm_1.invoke(
                    f"You are an experienced career counsellor. Based on the given job description, "
                    f"provide the key skills and ats keywords the candidates must have in their resume. "
                    f"Only output the key skills and ats keywords. job_description:{state['job_description']}"
                )
                return {"required_skills": response.skills, "required_keywords": response.keywords}

            def resume_parser(state: State):
                response = structured_llm_2.invoke(
                    f"You are an experienced career counsellor. Based on the given resume, "
                    f"provide the key skills and ats keywords present in the resume. "
                    f"Only output the key skills and ats keywords. resume:{state['resume']}"
                )
                return {"skills": response.skills, "keywords": response.keywords}

            def missing(state: State):
                prompt = f"""
        You are an expert career counsellor analyzing a resume against job requirements.
        
        Job Requirements:
        - Required Skills: {state.get('required_skills', [])}
        - Required Keywords: {state.get('required_keywords', [])}
        
        Resume Content:
        - Current Skills: {state.get('skills', [])}
        - Current Keywords: {state.get('keywords', [])}
        
        IMPORTANT MATCHING RULES:
        1. Consider skills SATISFIED if the resume contains related/specific implementations:
           - "Machine Learning" is satisfied by libraries like TensorFlow, PyTorch, Scikit-learn, Keras
           - "Data Science" is satisfied by Pandas, NumPy, Matplotlib, Seaborn
           - "Web Development" is satisfied by React, Angular, Vue.js, HTML, CSS, JavaScript
           - "Database" is satisfied by MySQL, PostgreSQL, MongoDB
           - "Cloud Computing" is satisfied by AWS, Azure, GCP
        
        2. Consider synonyms and variations as matches:
           - "Python programming" = "Python"
           - "JavaScript" = "JS"
           - "Machine Learning" = "ML"
           - "Artificial Intelligence" = "AI"
        
        3. Consider abbreviations and full forms as matches:
           - "React.js" = "ReactJS" = "React"
           - "Node.js" = "NodeJS" = "Node"
        
        4. A general skill is considered PRESENT if specific tools/libraries for that skill exist in resume.
        
        5. Only mark as MISSING if there's truly no evidence of the skill or related technologies.
        
        Analyze and identify ONLY the skills and keywords that are genuinely missing (no related evidence found).
        """
                response = structured_llm_3.invoke(prompt)
                return {"missing_skills": response.skills, "missing_keywords": response.keywords}

            def final_thoughts(state: State):
                prompt = f"""
                You are a senior career counselor and resume optimization expert with 15+ years of experience.
                
                ANALYSIS DATA:
                - Candidate's Current Skills: {state['skills']}
                - Job Required Skills: {state['required_skills']}
                - Missing Skills: {state.get('missing_skills', [])}
                - Missing ATS Keywords: {state.get('missing_keywords', [])}

                Based on above data, give the final feedback in brief.
                """
                response = llm.invoke(prompt)
                return {"final_thought": response.content}

            #****************************creating_graph********************************************************************************
            graph = StateGraph(State)
            graph.add_node("jd_checker", jd_parser)
            graph.add_node("resume_checker", resume_parser)
            graph.add_node("missing", missing)
            graph.add_node("feedback", final_thoughts)
            graph.set_entry_point("jd_checker")
            graph.add_edge("jd_checker", "resume_checker")
            graph.add_edge("resume_checker", "missing")
            graph.add_edge("missing", "feedback")
            graph.set_finish_point("feedback")
            workflow = graph.compile()

            #****************************Invoking_graph*********************************************
            result = workflow.invoke({"job_description": jd, "resume": text})

        # -------------------- Results Section --------------------
        st.subheader("🎯 Missing Skills")
        badges = " ".join(
            [
                f"<span style='background-color:#FFDDC1; padding:6px 12px; border-radius:12px; margin:4px; display:inline-block; font-weight:500;'>{skill}</span>"
                for skill in result['missing_skills']
            ]
        )
        st.markdown(badges, unsafe_allow_html=True)

        st.subheader("🧩 Recommended ATS Keywords")
        badges = " ".join(
            [
                f"<span style='background-color:#FFDDC1; padding:6px 12px; border-radius:12px; margin:4px; display:inline-block; font-weight:500;'>{keyword}</span>"
                for keyword in result['missing_keywords']
            ]
        )
        st.markdown(badges, unsafe_allow_html=True)

        st.subheader("📝 Final Thoughts")
        st.markdown(
            f"<div style='background-color:#F0F8FF; padding:15px; border-radius:10px;'>{result['final_thought']}</div>",
            unsafe_allow_html=True
        )
