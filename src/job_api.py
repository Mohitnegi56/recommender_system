
import os
from urllib.parse import quote_plus

import streamlit as st
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()


def get_secret(key):
    """Read a secret from Streamlit Secrets or environment variables."""
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(key)


def _fetch_actor_jobs(actor_id, run_input, api_token):
    """Run an Apify actor and return normalized job records."""
    token = api_token or get_secret("APIFY_API_TOKEN")

    if not token:
        raise ValueError(
            "Apify API token is missing. Add it to .env, "
            "Streamlit Secrets, or the sidebar."
        )

    try:
        client = ApifyClient(token)

        run = client.actor(actor_id).call(run_input=run_input)

        if not run or not run.get("defaultDatasetId"):
            raise RuntimeError(
                "Apify did not return a dataset for this run."
            )

        items = client.dataset(
            run["defaultDatasetId"]
        ).iterate_items()

        jobs = []

        for item in items:
            jobs.append({
                "title": (
                    item.get("title")
                    or item.get("positionName")
                    or "Title unavailable"
                ),
                "companyName": (
                    item.get("companyName")
                    or item.get("company")
                    or "Company unavailable"
                ),
                "location": (
                    item.get("location")
                    or item.get("jobLocation")
                    or "Location not specified"
                ),
                "link": (
                    item.get("link")
                    or item.get("url")
                    or item.get("jobUrl")
                    or ""
                ),
            })

        return jobs

    except Exception as exc:
        raise RuntimeError(
            f"Apify actor {actor_id} failed: {exc}"
        ) from exc


def fetch_linkedin_jobs(
    search_query, location="India", rows=60, api_token=None
):
    search_url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={quote_plus(search_query)}"
        f"&location={quote_plus(location)}"
    )

    run_input = {
        "urls": [{"url": search_url}]
    }

    # Note: rows is retained for compatibility with your main app.
    # This input does not enforce a result limit. Configure the
    # limit according to this actor's documented input schema.
    return _fetch_actor_jobs(
        "hKByXkMQaC5Qt9UMN",
        run_input,
        api_token,
    )


def fetch_naukri_jobs(
    search_query, location="India", rows=60, api_token=None
):
    run_input = {
        "keyword": search_query,
        "maxJobs": rows,
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all",
    }

    return _fetch_actor_jobs(
        "alpcnRV9YI9lYVPWk",
        run_input,
        api_token,
    )
