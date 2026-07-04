# 📄 AI Job Recommender & Career Analyzer

An AI-powered job recommendation and resume analysis system. Upload your resume to extract insights, discover skill gaps, create a personalized career roadmap, and fetch matching real-time job listings from LinkedIn and Naukri.

---

## 🔗 Live Application Link
🚀 **Try the app here:** [Live Link](https://recommendersystem-uvfuwzf964kyu5k25dpjm6.streamlit.app/)

---

## 🌟 Features

- **Resume Parsing & Extraction:** Automatically parses text from uploaded PDF resumes.
- **AI Career Analysis:** Powered by Llama 3.1 on Groq:
  - **Resume Summary:** Highlights key skills, education, and professional experience.
  - **Skill Gaps:** Analyzes the resume to find missing skills, certifications, and improvements.
  - **Future Roadmap:** Proposes a career strategy (skills to learn, industry exposure, etc.).
- **Smart Job Search:** Generates targeted search keywords based on the resume content.
- **Job Matching Aggregator:** Fetches matching jobs from:
  - **LinkedIn Jobs**
  - **Naukri Jobs (India)**
- **Model Context Protocol (MCP) Support:** Exposes fetching capabilities as tools via a FastMCP server for integration with LLM clients.

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **AI Orchestration:** Groq API (`llama-3.1-8b-instant`), LangChain, LangChain-Groq
- **Job Scraping/APIs:** Apify (LinkedIn & Naukri actors)
- **PDF Extraction:** PyMuPDF (fitz)
- **MCP Server Framework:** FastMCP

---

## 📋 Prerequisites

Before setting up the project, make sure you have:
1. **Python 3.11+** installed.
2. **Groq API Key:** Sign up at [Groq Console](https://console.groq.com/) to get an API key.
3. **Apify API Token:** Sign up at [Apify](https://apify.com) to get a token to run scraping actors.

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mohitnegi56/recommender_system.git
   cd recommender_system
   ```

2. **Set up a virtual environment and install dependencies:**
   *Using `uv` (recommended):*
   ```bash
   uv venv
   # On Windows (Command Prompt/PowerShell):
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   
   uv pip install -r requirements.txt
   ```
   *Using standard `pip`:*
   ```bash
   python -m venv .venv
   # On Windows (Command Prompt/PowerShell):
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   APIFY_API_TOKEN=your_apify_api_token_here
   ```

---

## 🚀 Running the Application

### 1. Web Application (Streamlit)
To start the interactive web application, run:
```bash
streamlit run app.py
```
Open the local URL displayed in the terminal (usually `http://localhost:8501`) in your browser.

### 2. FastMCP Server
To run the Model Context Protocol (MCP) server for integration with Cursor, Claude Desktop, or other agents:
```bash
python mcp_server.py
```
This runs the server using standard input/output (`stdio`) transport.

---

## 📂 File Structure

```text
recommender_system/
│
├── src/
│   ├── __init__.py
│   ├── helper.py          # PDF extraction and Groq API helper functions
│   └── job_api.py         # Apify integration for LinkedIn and Naukri jobs
│
├── app.py                 # Streamlit web application entrypoint
├── mcp_server.py          # FastMCP server exposing tools
├── pyproject.toml         # Project configuration and dependency listing
├── requirements.txt       # Project dependencies list
├── .gitignore             # Git ignored files (including .env)
└── README.md              # Project documentation
```
