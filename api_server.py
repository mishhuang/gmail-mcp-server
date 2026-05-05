"""FastAPI REST server exposing Gmail operations for the frontend."""

import os
import json
import logging
from typing import Optional, List
import anthropic
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from src.config import ALLOW_WRITE
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


ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL_NAME", "claude-sonnet-4-6")

DIGEST_SYSTEM_PROMPT = """You are synthesizing AI/tech newsletter content into a single unified digest.
Organize by topic. Use ## for topic headings and ### for sub-points.
Include ALL unique information and perspectives from all newsletters.
Merge overlapping stories into one entry, preserving distinct viewpoints and details.
Eliminate pure repetition. Write as a single coherent article, not a list of summaries."""


class DigestRequest(BaseModel):
    hours_back: int = 24
    senders: Optional[List[str]] = None


@app.post("/newsletters/digest")
async def newsletter_digest(
    request: DigestRequest,
    gc: GmailClient = Depends(get_gmail_client),
):
    newsletters = fetch_newsletters_func(
        service=gc.service,
        hours_back=request.hours_back,
        senders=request.senders,
    )

    if newsletters["total_emails"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No newsletters found in the past {request.hours_back} hours."
        )

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not set in .env")

    parts = []
    for sender_email, emails in newsletters["newsletters_by_sender"].items():
        for email in emails:
            parts.append(f"### {email['subject']}\n\n{email['content']}")

    combined = "\n\n---\n\n".join(parts)

    def generate():
        anthropic_client = anthropic.Anthropic(api_key=api_key)
        with anthropic_client.messages.stream(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            system=DIGEST_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"Here are the newsletters from the past {request.hours_back} hours:\n\n"
                    f"{combined}\n\nWrite the unified digest now."
                ),
            }],
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _write_check():
    if not ALLOW_WRITE:
        raise HTTPException(
            status_code=403,
            detail="Write operations are disabled. Set ALLOW_WRITE=true in .env to enable."
        )


@app.put("/emails/{message_id}/read")
async def mark_read(message_id: str, gc: GmailClient = Depends(get_gmail_client)):
    _write_check()
    result = gc.mark_as_read(message_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to mark email as read")
    return {"success": True}


@app.put("/emails/{message_id}/unread")
async def mark_unread(message_id: str, gc: GmailClient = Depends(get_gmail_client)):
    _write_check()
    result = gc.mark_as_unread(message_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to mark email as unread")
    return {"success": True}


@app.post("/emails/{message_id}/archive")
async def archive_email(message_id: str, gc: GmailClient = Depends(get_gmail_client)):
    _write_check()
    result = gc.archive_email(message_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to archive email")
    return {"success": True}


@app.post("/emails/{message_id}/delete")
async def delete_email(message_id: str, gc: GmailClient = Depends(get_gmail_client)):
    _write_check()
    result = gc.delete_email(message_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to delete email")
    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=API_PORT, reload=True)
