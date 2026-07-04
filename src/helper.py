import os
import fitz
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_secret(key):
    # Streamlit Cloud
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        # Local development with .env
        return os.getenv(key)


GROQ_API_KEY = get_secret("GROQ_API_KEY")


def ask_groq(prompt, max_tokens=500, api_key=None):
    key = api_key or GROQ_API_KEY
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
