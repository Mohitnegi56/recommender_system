import fitz
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from groq import RateLimitError


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in doc:
        text += page.get_text()

    return text


def ask_groq(prompt, max_tokens=500):

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.5,
        max_tokens=max_tokens,
        api_key=GROQ_API_KEY
    )

    try:
        response = llm.invoke(prompt)
        return response.content

    except RateLimitError:
        return (
            "Groq API rate limit reached. "
            "Please wait a few minutes and try again."
        )