"""FastAPI REST server exposing Gmail operations for the frontend."""

import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.gmail_client import GmailClient

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=API_PORT, reload=True)
