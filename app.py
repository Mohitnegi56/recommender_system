
import os
import html
import hashlib
import streamlit as st
from dotenv import load_dotenv

from src.helper import extract_text_from_pdf, ask_groq, get_secret
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs

load_dotenv()

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI Job Recommender",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
defaults = {
    "resume_text": "",
    "resume_hash": "",
    "resume_summary": "",
    "skills": [],
    "skill_gaps": [],
    "roadmap": "",
    "jobs": [],
    "saved_jobs": [],
    "analysis_done": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #10182B;
    --panel: #172238;
    --purple: #8B7CFF;
    --muted: #91A0B8;
    --border: rgba(148, 163, 184, 0.18);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0B1120;
    color: #F4F7FC;
}

[data-testid="stSidebar"] {
    background: #10182B;
    border-right: 1px solid rgba(255,255,255,0.07);
}

[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1600px;
}

h1, h2, h3 {
    color: #F4F7FC !important;
    letter-spacing: -0.5px;
}

p, label, .stMarkdown {
    color: #C6D0E0;
}

.brand {
    font-size: 23px;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 4px;
}

.brand-sub {
    color: #91A0B8;
    font-size: 12px;
    margin-bottom: 30px;
}

.section-label {
    color: #8494AD;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
    margin: 20px 0 8px;
}

.hero {
    padding: 32px 34px;
    border-radius: 22px;
    background:
      radial-gradient(ellipse at 85% 15%, rgba(139,124,255,.45), transparent 38%),
      radial-gradient(ellipse at 70% 100%, rgba(43,120,210,.35), transparent 40%),
      linear-gradient(120deg, #202B50 0%, #332D68 55%, #182A4D 100%);
    border: 1px solid rgba(255,255,255,.12);
    margin-bottom: 25px;
    min-height: 220px;
}

.hero-tag {
    display: inline-block;
    padding: 6px 11px;
    border: 1px solid rgba(255,255,255,.22);
    background: rgba(255,255,255,.08);
    color: #D9D5FF;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 15px;
}

.hero h1 {
    font-size: clamp(28px, 3vw, 40px);
    line-height: 1.15;
    margin: 0 0 12px;
}

.hero p {
    color: #D2D9ED;
    max-width: 600px;
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 0;
}

.hero-features {
    margin-top: 23px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.hero-feature {
    color: #E5E7FF;
    font-size: 11px;
    padding: 8px 10px;
    border-radius: 8px;
    background: rgba(255,255,255,.08);
}

.panel {
    background: #121D31;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 21px;
    margin-bottom: 18px;
}

.panel-title {
    font-size: 16px;
    font-weight: 700;
    color: #F4F7FC;
    margin-bottom: 5px;
}

.panel-subtitle {
    color: #91A0B8;
    font-size: 12px;
    margin-bottom: 18px;
}

.metric {
    background: linear-gradient(145deg, #162239, #111B2E);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 18px;
    min-height: 120px;
}

.metric-icon {
    font-size: 20px;
    margin-bottom: 12px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 800;
    line-height: 1.2;
}

.metric-label {
    color: #91A0B8;
    font-size: 12px;
    margin-top: 6px;
}

.skill-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    margin: 13px 0 6px;
    color: #DDE5F3;
}

.skill-track {
    height: 6px;
    background: #27344B;
    border-radius: 10px;
    overflow: hidden;
}

.skill-fill {
    height: 100%;
    background: linear-gradient(90deg, #8B7CFF, #57B8FF);
    border-radius: 10px;
}

.gap-card {
    background: #18243A;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px;
    margin: 10px 0;
}

.gap-title {
    color: #F2F5FC;
    font-weight: 700;
    font-size: 13px;
}

.gap-desc {
    color: #9AAAC0;
    font-size: 12px;
    margin-top: 5px;
    line-height: 1.6;
}

.job-card {
    background: #121D31;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 18px;
    margin: 12px 0;
}

.job-title {
    color: #F4F7FC;
    font-size: 16px;
    font-weight: 700;
}

.job-company {
    color: #B4C0D3;
    font-size: 12px;
    margin-top: 5px;
}

.job-meta {
    color: #91A0B8;
    font-size: 12px;
    margin-top: 12px;
    line-height: 1.8;
}

.job-badge {
    display: inline-block;
    color: #B9B0FF;
    background: rgba(139,124,255,.12);
    border: 1px solid rgba(139,124,255,.2);
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 10px;
    margin: 4px 4px 0 0;
}

.stButton > button {
    border-radius: 9px;
    border: 1px solid rgba(139,124,255,.45);
    background: linear-gradient(100deg, #7968EF, #6254D9);
    color: white;
    font-weight: 600;
    padding: 0.55rem 1rem;
    transition: 0.2s;
}

.stButton > button:hover {
    border-color: #B5ACFF;
    background: #786BEA;
    color: white;
}

.stTextInput input, .stSelectbox div[data-baseweb="select"],
.stTextArea textarea {
    background-color: #121D31;
    color: #F4F7FC;
    border-color: var(--border);
}

[data-testid="stFileUploader"] {
    background: #121D31;
    border: 1px dashed #596783;
    border-radius: 12px;
    padding: 12px;
}

hr {
    border-color: rgba(148,163,184,.15);
}

div[data-testid="stTabs"] button {
    color: #A9B6CB;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #B8AEFF;
}

.small-muted {
    font-size: 12px;
    color: #91A0B8;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def safe_text(value):
    """Escape text before inserting it into HTML."""
    return html.escape(str(value or ""))


def metric_card(icon, value, label):
    st.markdown(f"""
    <div class="metric">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{safe_text(value)}</div>
        <div class="metric-label">{safe_text(label)}</div>
    </div>
    """, unsafe_allow_html=True)


def parse_list(text):
    """Parse a simple comma/newline-separated AI response."""
    if not text:
        return []

    result = []
    for line in text.replace("•", "\n").splitlines():
        line = line.strip().lstrip("-*0123456789. ").strip()
        if line and line not in result:
            result.append(line)

    return result


def job_value(job, *keys, default="Not specified"):
    """Support slightly different field names from different job actors."""
    for key in keys:
        value = job.get(key)
        if value:
            return str(value)
    return default


def render_job_card(job, index, source="Job board"):
    title = job_value(job, "title", "jobTitle", "positionName",
                      default="Job title unavailable")
    company = job_value(job, "companyName", "company", "company_name",
                        default="Company not listed")
    location = job_value(job, "location", "jobLocation",
                         default="Location not specified")
    url = job_value(job, "link", "url", "jobUrl",
                    default="")

    st.markdown(f"""
    <div class="job-card">
        <div class="job-title">{safe_text(title)}</div>
        <div class="job-company">{safe_text(company)}</div>
        <div class="job-meta">
            📍 {safe_text(location)}<br>
            🔎 Source: {safe_text(source)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if url.startswith(("https://", "http://")):
            st.link_button("View job ↗", url, key=f"view_{source}_{index}")
        else:
            st.caption("Job link not available")

    with col2:
        saved_links = {
            job_value(j, "link", "url", "jobUrl", default="")
            for j in st.session_state.saved_jobs
        }
        if url and url in saved_links:
            st.button("✓ Saved", key=f"saved_{source}_{index}",
                      disabled=True, use_container_width=True)
        elif st.button("☆ Save job", key=f"save_{source}_{index}",
                       use_container_width=True):
            if url:
                st.session_state.saved_jobs.append(job)
                st.success("Job saved!")
                st.rerun()
            else:
                st.warning("This job has no link to save.")


def make_demo_jobs():
    return [
        {
            "title": "Machine Learning Intern",
            "companyName": "Google",
            "location": "Bengaluru, India",
            "link": "https://careers.google.com/",
            "source": "LinkedIn",
        },
        {
            "title": "Data Science Intern",
            "companyName": "Microsoft",
            "location": "Hyderabad, India",
            "link": "https://careers.microsoft.com/",
            "source": "LinkedIn",
        },
        {
            "title": "AI/ML Intern",
            "companyName": "Amazon",
            "location": "Bengaluru, India",
            "link": "https://www.amazon.jobs/",
            "source": "Naukri",
        },
        {
            "title": "Python Developer Intern",
            "companyName": "Adobe",
            "location": "Noida, India",
            "link": "https://careers.adobe.com/",
            "source": "Naukri",
        },
        {
            "title": "Data Analyst Intern",
            "companyName": "Infosys",
            "location": "Pune, India",
            "link": "https://www.infosys.com/careers/",
            "source": "Naukri",
        },
    ]


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand">🚀 CareerPilot AI</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="brand-sub">Your personal AI career assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-label">Workspace</div>',
                unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Resume Analysis",
            "Skill Gaps",
            "Career Roadmap",
            "Job Recommendations",
            "Saved Jobs",
            "Settings",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<div class="section-label">API Configuration</div>',
                unsafe_allow_html=True)

    groq_key = st.text_input(
        "Groq API key",
        value="",
        type="password",
        placeholder="Enter Groq API key",
        help="Leave blank to use GROQ_API_KEY from your .env or Streamlit secrets."
    )

    apify_key = st.text_input(
        "Apify API token",
        value="",
        type="password",
        placeholder="Enter Apify token",
        help="Leave blank to use APIFY_API_TOKEN from your .env or secrets."
    )

    if st.button("Clear analysis", use_container_width=True):
        for key in [
            "resume_text", "resume_hash", "resume_summary", "skills",
            "skill_gaps", "roadmap", "jobs"
        ]:
            st.session_state[key] = defaults[key]
        st.session_state.analysis_done = False
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div class="small-muted">AI-powered career planning<br>Built with Streamlit</div>',
        unsafe_allow_html=True
    )


# --------------------------------------------------
# HEADER / HERO
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-tag">✦ YOUR AI CAREER COMPANION</div>
    <h1>Turn your skills into<br>your next opportunity.</h1>
    <p>
        Analyze your resume, discover skill gaps, build a learning roadmap,
        and find job opportunities that align with your career goals.
    </p>
    <div class="hero-features">
        <span class="hero-feature">✧ Resume Analysis</span>
        <span class="hero-feature">✧ Skill Gap Detection</span>
        <span class="hero-feature">✧ Career Roadmap</span>
        <span class="hero-feature">✧ Live Job Search</span>
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------
st.markdown("## Your career dashboard")
st.markdown(
    '<p class="small-muted">An overview of your resume and job search.</p>',
    unsafe_allow_html=True
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("📄", "01" if st.session_state.analysis_done else "00",
                "Resume analyzed")
with m2:
    metric_card("✦", len(st.session_state.skills),
                "Skills identified")
with m3:
    metric_card("🎯", len(st.session_state.skill_gaps),
                "Skill gaps found")
with m4:
    metric_card("💼", len(st.session_state.jobs),
                "Jobs retrieved")

st.write("")


# --------------------------------------------------
# RESUME UPLOAD AND ANALYSIS
# --------------------------------------------------
if page in ["Dashboard", "Resume Analysis"]:
    left, right = st.columns([1, 1.15], gap="large")

    with left:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">📄 Upload your resume</div>
            <div class="panel-subtitle">
                Upload a PDF to start your personalized career analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose your resume",
            type=["pdf"],
            help="PDF format only.",
            label_visibility="collapsed",
        )

        if uploaded_file:
            file_bytes = uploaded_file.getvalue()
            current_hash = hashlib.sha256(file_bytes).hexdigest()

            if current_hash != st.session_state.resume_hash:
                st.session_state.resume_hash = current_hash
                st.session_state.analysis_done = False
                st.session_state.resume_text = ""
                st.session_state.resume_summary = ""
                st.session_state.skills = []
                st.session_state.skill_gaps = []
                st.session_state.roadmap = ""
                st.session_state.jobs = []

            st.success(f"Uploaded: {uploaded_file.name}")

            if st.button("✨ Analyze my resume", use_container_width=True):
                with st.spinner("Reading your resume..."):
                    try:
                        resume_text = extract_text_from_pdf(uploaded_file)

                        if not resume_text or not resume_text.strip():
                            st.error(
                                "No text was found. If this is a scanned PDF, "
                                "you may need OCR."
                            )
                        else:
                            st.session_state.resume_text = resume_text

                            with st.spinner("Generating your career insights..."):
                                summary = ask_groq(
                                    "Analyze this resume. Give a concise summary "
                                    "of the candidate's profile, education, "
                                    "experience, projects, and strengths.\n\n"
                                    + resume_text,
                                    api_key=groq_key or None,
                                )

                                skills = ask_groq(
                                    "Identify the technical and professional "
                                    "skills explicitly supported by this resume. "
                                    "Return a simple bullet list. Do not invent "
                                    "skills.\n\n" + resume_text,
                                    api_key=groq_key or None,
                                )

                                gaps = ask_groq(
                                    "Assume the candidate wants to pursue "
                                    "AI/ML, data science, and Python development "
                                    "internships. Identify important skills "
                                    "that appear missing or insufficiently "
                                    "demonstrated in the resume. Return a "
                                    "bullet list, with a short reason for each. "
                                    "Do not claim that a skill is missing if "
                                    "the resume clearly demonstrates it.\n\n"
                                    + resume_text,
                                    api_key=groq_key or None,
                                )

                                roadmap = ask_groq(
                                    "Create a practical 4-stage career roadmap "
                                    "for this candidate. Include what to learn, "
                                    "one practical project, and an outcome for "
                                    "each stage. Use simple language.\n\n"
                                    + resume_text,
                                    api_key=groq_key or None,
                                )

                            st.session_state.resume_summary = str(summary)
                            st.session_state.skills = parse_list(str(skills))
                            st.session_state.skill_gaps = parse_list(str(gaps))
                            st.session_state.roadmap = str(roadmap)
                            st.session_state.analysis_done = True
                            st.success("Resume analysis completed!")
                            st.rerun()

                    except Exception as e:
                        st.error(f"Resume analysis failed: {e}")

    with right:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">✨ Resume insights</div>
            <div class="panel-subtitle">
                Your AI-generated profile and recommendations.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.analysis_done:
            tab1, tab2, tab3 = st.tabs(
                ["Summary", "Skills", "Skill gaps"]
            )

            with tab1:
                st.markdown("### Candidate summary")
                st.write(st.session_state.resume_summary)

            with tab2:
                st.markdown("### Skills identified")
                for skill in st.session_state.skills:
                    st.markdown(f"- {skill}")

            with tab3:
                st.markdown("### Areas to improve")
                for gap in st.session_state.skill_gaps:
                    st.markdown(f"- {gap}")
        else:
            st.info(
                "Upload a resume and click **Analyze my resume** "
                "to see your personalized insights here."
            )


# --------------------------------------------------
# SKILLS OVERVIEW
# --------------------------------------------------
if page == "Dashboard":
    st.write("")
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">📊 Skills overview</div>
            <div class="panel-subtitle">
                Skills extracted from your resume.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.skills:
            for i, skill in enumerate(st.session_state.skills[:8]):
                # These bars are visual indicators, not AI-measured proficiency.
                percentage = max(35, 90 - i * 7)
                st.markdown(f"""
                <div class="skill-row">
                    <span>{safe_text(skill)}</span>
                    <span>{percentage}%</span>
                </div>
                <div class="skill-track">
                    <div class="skill-fill" style="width:{percentage}%"></div>
                </div>
                """, unsafe_allow_html=True)
            st.caption(
                "Illustrative bars only. They do not measure actual proficiency."
            )
        else:
            st.info("Your skills will appear here after resume analysis.")

    with col2:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">🎯 Priority skill gaps</div>
            <div class="panel-subtitle">
                Focus areas to consider for your target roles.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.skill_gaps:
            for gap in st.session_state.skill_gaps[:4]:
                st.markdown(f"""
                <div class="gap-card">
                    <div class="gap-title">↗ {safe_text(gap)}</div>
                    <div class="gap-desc">
                        Review this area and practice it through a project.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Analyze your resume to generate skill-gap suggestions.")


# --------------------------------------------------
# CAREER ROADMAP
# --------------------------------------------------
if page == "Career Roadmap":
    st.markdown("## 🧭 Your career roadmap")
    st.markdown(
        '<p class="small-muted">A structured plan based on your resume.</p>',
        unsafe_allow_html=True
    )

    if st.session_state.roadmap:
        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )
        st.markdown(st.session_state.roadmap)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info(
            "Analyze your resume first. Your personalized roadmap will "
            "appear here."
        )


# --------------------------------------------------
# SKILL GAPS PAGE
# --------------------------------------------------
if page == "Skill Gaps":
    st.markdown("## 🎯 Skill gap analysis")
    st.markdown(
        '<p class="small-muted">Use these suggestions to guide your learning.</p>',
        unsafe_allow_html=True
    )

    if st.session_state.skill_gaps:
        for i, gap in enumerate(st.session_state.skill_gaps, start=1):
            with st.container(border=True):
                st.markdown(f"### {i}. {gap}")
                st.write(
                    "Suggested action: study the fundamentals, complete a "
                    "small hands-on project, and add the result to your portfolio."
                )
    else:
        st.info("Analyze your resume to generate skill-gap suggestions.")


# --------------------------------------------------
# JOB RECOMMENDATIONS
# --------------------------------------------------
if page in ["Dashboard", "Job Recommendations"]:
    st.write("")
    st.markdown("## 💼 Job recommendations")
    st.markdown(
        '<p class="small-muted">Search job boards using your preferred filters.</p>',
        unsafe_allow_html=True
    )

    f1, f2, f3 = st.columns(3)

    with f1:
        keyword = st.text_input(
            "Job title or keyword",
            value="Machine Learning Intern",
            placeholder="e.g. Data Analyst",
        )

    with f2:
        location = st.text_input(
            "Location",
            value="India",
            placeholder="e.g. Bengaluru",
        )

    with f3:
        number_of_jobs = st.selectbox(
            "Number of jobs",
            [5, 10, 15, 20],
            index=1,
        )

    source_filter = st.selectbox(
        "Job source",
        ["All sources", "LinkedIn", "Naukri", "Demo data"],
    )

    search_col, demo_col = st.columns([1, 1])

    with search_col:
        search_clicked = st.button(
            "🔍 Find matching jobs",
            use_container_width=True,
        )

    with demo_col:
        demo_clicked = st.button(
            "Preview demo jobs",
            use_container_width=True,
        )

    if search_clicked:
        jobs = []
        api_token = apify_key or get_secret("APIFY_API_TOKEN")

        if source_filter == "Demo data":
            jobs = make_demo_jobs()
        else:
            if not api_token:
                st.error(
                    "Add your Apify token in the sidebar or set "
                    "APIFY_API_TOKEN in your .env file."
                )
            else:
                try:
                    if source_filter in ["All sources", "LinkedIn"]:
                        with st.spinner("Searching LinkedIn jobs..."):
                            linkedin_jobs = fetch_linkedin_jobs(
                                keyword,
                                api_key=api_token,
                                rows=number_of_jobs,
                            )
                            for job in linkedin_jobs or []:
                                job = dict(job)
                                job["source"] = "LinkedIn"
                                jobs.append(job)
                except Exception as e:
                    st.warning(f"LinkedIn search failed: {e}")

                try:
                    if source_filter in ["All sources", "Naukri"]:
                        with st.spinner("Searching Naukri jobs..."):
                            naukri_jobs = fetch_naukri_jobs(
                                keyword,
                                api_key=api_token,
                                rows=number_of_jobs,
                            )
                            for job in naukri_jobs or []:
                                job = dict(job)
                                job["source"] = "Naukri"
                                jobs.append(job)
                except Exception as e:
                    st.warning(f"Naukri search failed: {e}")

        # Simple location filter
        if location.strip() and location.lower() != "anywhere":
            jobs = [
                j for j in jobs
                if location.lower() in job_value(
                    j, "location", "jobLocation", default=""
                ).lower()
                or location.lower() == "india"
            ]

        # Remove duplicates by link
        unique_jobs = []
        seen = set()
        for job in jobs:
            link = job_value(job, "link", "url", "jobUrl", default="")
            identity = link or (
                job_value(job, "title", "jobTitle", default="").lower()
                + job_value(job, "companyName", "company", default="").lower()
            )
            if identity and identity not in seen:
                seen.add(identity)
                unique_jobs.append(job)

        st.session_state.jobs = unique_jobs

    if demo_clicked:
        st.session_state.jobs = make_demo_jobs()

    jobs = st.session_state.jobs

    if jobs:
        st.markdown(
            f'<p class="small-muted">Showing {len(jobs)} job listings. '
            'Check each employer\'s official website for current availability.</p>',
            unsafe_allow_html=True
        )

        tab_all, tab_linkedin, tab_naukri = st.tabs(
            ["All jobs", "LinkedIn", "Naukri"]
        )

        with tab_all:
            for i, job in enumerate(jobs):
                render_job_card(
                    job, i, job.get("source", "Job board")
                )

        with tab_linkedin:
            filtered = [
                j for j in jobs
                if j.get("source") == "LinkedIn"
            ]
            if not filtered:
                st.info("No LinkedIn results in the current search.")
            for i, job in enumerate(filtered):
                render_job_card(job, i, "LinkedIn")

        with tab_naukri:
            filtered = [
                j for j in jobs
                if j.get("source") == "Naukri"
            ]
            if not filtered:
                st.info("No Naukri results in the current search.")
            for i, job in enumerate(filtered):
                render_job_card(job, i, "Naukri")
    else:
        st.info(
            "Your job recommendations will appear here. "
            "Click **Preview demo jobs** to test the interface."
        )


# --------------------------------------------------
# SAVED JOBS
# --------------------------------------------------
if page == "Saved Jobs":
    st.markdown("## ⭐ Saved jobs")
    st.markdown(
        '<p class="small-muted">Keep track of opportunities you want to revisit.</p>',
        unsafe_allow_html=True
    )

    if st.session_state.saved_jobs:
        for i, job in enumerate(st.session_state.saved_jobs):
            title = job_value(job, "title", "jobTitle",
                              default="Job title unavailable")
            company = job_value(job, "companyName", "company",
                                default="Company not listed")
            st.markdown(f"### {safe_text(title)}")
            st.caption(company)

            url = job_value(job, "link", "url", "jobUrl", default="")
            if url.startswith(("https://", "http://")):
                st.link_button("Open job ↗", url, key=f"saved_open_{i}")

            if st.button("Remove saved job", key=f"remove_saved_{i}"):
                st.session_state.saved_jobs.pop(i)
                st.rerun()

            st.divider()
    else:
        st.info(
            "No saved jobs yet. Go to Job Recommendations and save a job."
        )


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------
if page == "Settings":
    st.markdown("## ⚙️ Settings")

    st.markdown("""
    <div class="panel">
        <div class="panel-title">Application information</div>
        <div class="panel-subtitle">
            Manage your local setup and API configuration.
        </div>
        <p>• Frontend: Streamlit</p>
        <p>• Resume extraction: PyMuPDF</p>
        <p>• AI analysis: Groq</p>
        <p>• Job search: Apify actors</p>
    </div>
    """, unsafe_allow_html=True)

    st.warning(
        "API keys entered in the sidebar are used for this app session. "
        "For deployment, configure secrets securely and never commit API keys "
        "to GitHub."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(
    '<p class="small-muted" style="text-align:center;">'
    'CareerPilot AI · Built with Streamlit · '
    'AI-generated suggestions should be reviewed before making career decisions.'
    '</p>',
    unsafe_allow_html=True
)