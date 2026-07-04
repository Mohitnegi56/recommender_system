import os
from urllib.parse import quote_plus
import streamlit as st
from dotenv import load_dotenv
from apify_client import ApifyClient


load_dotenv()


def get_secret(key):
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key)


APIFY_API_TOKEN = get_secret("APIFY_API_TOKEN")

client = ApifyClient(APIFY_API_TOKEN)

def fetch_linkedin_jobs(search_query, location="India", rows=60):

    search_url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={quote_plus(search_query)}"
        f"&location={quote_plus(location)}"
    )

    run_input = {
        "urls": [
            {
                "url": search_url
            }
        ]
    }

    run = client.actor(
        "hKByXkMQaC5Qt9UMN"
    ).call(run_input=run_input)

    jobs = list(
    client.dataset(
        run.default_dataset_id
    ).iterate_items()
)

    return jobs


def fetch_naukri_jobs(search_query, location="India", rows=60):
    run_input = {
        "keyword": search_query,
        "maxJobs": rows,
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all"
    }

    run = client.actor(
        "alpcnRV9YI9lYVPWk"
    ).call(run_input=run_input)

    jobs = list(
    client.dataset(
        run.default_dataset_id
    ).iterate_items()
)

    return jobs