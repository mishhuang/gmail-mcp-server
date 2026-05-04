"""FastAPI REST server exposing Gmail operations for the frontend."""

import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.gmail_client import GmailClient
from src.newsletter import (
    fetch_newsletters as fetch_newsletters_func,
    NEWSLETTER_SENDERS,
    calculate_date_filter,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_PORT = int(os.getenv("API_PORT", "8000"))

app = FastAPI(title="Gmail API Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_gmail_client = GmailClient()


def get_gmail_client() -> GmailClient:
    if not _gmail_client.service:
        if not _gmail_client.authenticate():
            raise HTTPException(
                status_code=503,
                detail="Gmail authentication failed. Run: python authenticate.py"
            )
    return _gmail_client


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/emails")
async def list_emails(
    q: str = "",
    max_results: int = 20,
    gc: GmailClient = Depends(get_gmail_client),
):
    summaries = gc.get_email_summaries(query=q, max_results=max_results)
    return {"emails": summaries}


@app.get("/emails/{message_id}")
async def read_email(
    message_id: str,
    gc: GmailClient = Depends(get_gmail_client),
):
    email = gc.get_parsed_email(message_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@app.get("/newsletters")
async def list_newsletters(
    hours_back: int = 24,
    gc: GmailClient = Depends(get_gmail_client),
):
    senders = list(NEWSLETTER_SENDERS.values())
    date_filter = calculate_date_filter(hours_back)
    sender_query = " OR ".join(f"from:{s}" for s in senders)
    query = f"({sender_query}) after:{date_filter}"
    summaries = gc.get_email_summaries(query=query, max_results=50)
    return {"emails": summaries, "total": len(summaries)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=API_PORT, reload=True)
