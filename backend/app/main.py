from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Subject Guide AI"),
    description="AI-powered Subject Guide and Question Bank Assistant",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Subject Guide AI backend is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }