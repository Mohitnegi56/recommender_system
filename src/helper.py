import os
import fitz
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_secret(key):
    # Streamlit Cloud or local secrets
    try:
        return st.secrets[key]
    except Exception:
        # Local development with .env or environment variable
        return os.getenv(key)


def ask_groq(prompt, max_tokens=500, api_key=None):
    key = api_key or get_secret("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "Groq API Key is not set. Please add it to your environment variables, "
            "Streamlit Secrets, or input it in the sidebar."
        )

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.5,
        max_tokens=max_tokens,
        api_key=key
    )

    response = llm.invoke(prompt)

    return response.content


def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in doc:
        text += page.get_text()

    return text
