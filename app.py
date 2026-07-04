import streamlit as st
from src.helper import extract_text_from_pdf, ask_groq
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs

st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("📄AI Job Recommender")
st.markdown("Upload your resume and get job recommendations based on your skills and experience from LinkedIn and Naukri.")

# API Configuration Sidebar
groq_key = None
apify_token = None

with st.sidebar:
    st.header("🔑 API Configurations")
    from src.helper import GROQ_API_KEY
    from src.job_api import APIFY_API_TOKEN
    
    # Check/Request Groq API Key
    if not GROQ_API_KEY:
        groq_key = st.text_input("Enter Groq API Key:", type="password", help="Needed to analyze your resume.")
        if not groq_key:
            st.warning("⚠️ Groq API Key is required to analyze your resume.")
    else:
        st.success("✅ Groq API Key is loaded!")
        groq_key = GROQ_API_KEY
        
    # Check/Request Apify Token
    if not APIFY_API_TOKEN:
        apify_token = st.text_input("Enter Apify API Token:", type="password", help="Needed to fetch live jobs from LinkedIn/Naukri.")
        if not apify_token:
            st.info("💡 Enter Apify Token to enable job recommendations.")
    else:
        st.success("✅ Apify API Token is loaded!")
        apify_token = APIFY_API_TOKEN

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    if not groq_key:
        st.error("❌ Missing Groq API Key. Please enter your Groq API Key in the sidebar to analyze your resume.")
        st.stop()

    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    with st.spinner("Summarizing your resume..."):
        summary = ask_groq(
            f"Summarize this resume highlighting the skills, education, and experience: \n\n{resume_text}",
            max_tokens=500,
            api_key=groq_key
        )

    with st.spinner("Finding skill Gaps..."):
        gaps = ask_groq(
            f"Analyze this resume and highlight missing skills, certifications, and experiences needed for better job opportunities: \n\n{resume_text}",
            max_tokens=400,
            api_key=groq_key
        )

    with st.spinner("Creating Future Roadmap..."):
        roadmap = ask_groq(
            f"Based on this resume, suggest a future roadmap to improve this person's career prospects (Skill to learn, certification needed, industry exposure): \n\n{resume_text}",
            max_tokens=400,
            api_key=groq_key
        )
    
    # Display nicely formatted results
    st.markdown("---")
    st.header("📑 Resume Summary")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{summary}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{gaps}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🚀 Future Roadmap & Preparation Strategy")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{roadmap}</div>", unsafe_allow_html=True)

    st.success("✅ Analysis Completed Successfully!")

    if st.button("🔎Get Job Recommendations"):
        if not apify_token:
            st.error("❌ Missing Apify API Token. Please enter your Apify Token in the sidebar to search for jobs.")
            st.stop()

        with st.spinner("Fetching job recommendations..."):
            keywords = ask_groq(
                f"Based on this resume summary, suggest the best job titles and keywords for searching jobs. Give a comma-separated list only, no explanation.\n\nSummary: {summary}",
                max_tokens=100,
                api_key=groq_key
            )

            search_keywords_clean = keywords.replace("\n", "").strip()

        st.success(f"Extracted Job Keywords: {search_keywords_clean}")

        with st.spinner("Fetching jobs from LinkedIn and Naukri..."):
            linkedin_jobs = fetch_linkedin_jobs(search_keywords_clean, rows=60, api_token=apify_token)
            naukri_jobs = fetch_naukri_jobs(search_keywords_clean, rows=60, api_token=apify_token)

        st.markdown("---")
        st.header("💼 Top LinkedIn Jobs")

        if linkedin_jobs:
            for job in linkedin_jobs:
                st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
                st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗 [View Job]({job.get('link')})")
                st.markdown("---")
        else:
            st.warning("No LinkedIn jobs found.")

        st.markdown("---")
        st.header("💼 Top Naukri Jobs (India)")

        if naukri_jobs:
            for job in naukri_jobs:
                st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
                st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗 [View Job]({job.get('url')})")
                st.markdown("---")
        else:
            st.warning("No Naukri jobs found.")