# Subject Guide AI — Subject Guide & Question Bank Assistant

An AI-powered academic study assistant that helps students understand their study materials, solve questions, generate practice content, and prepare for examinations.

## 🎯 Problem

Students often have to search through multiple notes, textbooks, and previous-year question papers to find answers and prepare for exams.

This makes studying time-consuming and difficult, especially when academic resources are scattered across different documents.

## 💡 Solution

Subject Guide AI converts a student's academic materials into an interactive AI-powered study assistant.

Students can upload:

- Notes
- Textbooks
- Previous-Year Question Papers
- Other academic materials

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant content and generate source-grounded answers.

## 🚀 Core Features

- Multi-document upload
- RAG-based question answering
- Source and page citations
- AI Subject Guide
- Question Bank Generator
- Previous-Year Question Analysis
- AI Quiz and Mock Test Generator
- Exam Mode for 2, 5, and 10 mark answers
- Weak Topic Detection
- Personalized Study Planner

## 🤖 AI Capabilities

The architecture supports multiple AI providers:

- Gemini — Cloud AI
- Ollama + Qwen3 — Local AI

This allows the system to support both cloud-based and local AI workflows.

## 🧠 RAG Pipeline

    Academic Documents
            ↓
    Document Processing
            ↓
    Text Chunking
            ↓
    Embeddings
            ↓
    Vector Database
            ↓
    Semantic Search
            ↓
    Relevant Context
            ↓
    AI Model
            ↓
    Grounded Answer
            ↓
    Source Citation

## 🏗️ Project Structure

    subject-guide-ai/
    ├── backend/
    │   ├── app/
    │   │   ├── api/
    │   │   ├── core/
    │   │   ├── models/
    │   │   ├── services/
    │   │   ├── utils/
    │   │   ├── __init__.py
    │   │   └── main.py
    │   └── tests/
    │
    ├── docs/
    │   ├── architecture.md
    │   └── features.md
    │
    ├── frontend/
    │   └── README.md
    │
    ├── tests/
    │
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── requirements.txt

## ⚙️ Current Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv

### AI

- Google Gemini
- Ollama
- Qwen3

### RAG

- Document processing
- Text extraction
- Text chunking
- Embeddings
- Vector database
- Semantic search
- Source-grounded generation

### Development

- Git
- GitHub
- Visual Studio Code

## 🔐 Configuration

Environment variables are used for sensitive configuration.

Example:

    APP_NAME=Subject Guide AI
    APP_ENV=development
    AI_PROVIDER=gemini
    GEMINI_API_KEY=
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL=qwen3:0.6b

The `.env` file should never be committed to GitHub.

Only `.env.example` should be included in the repository.

## 📚 Documentation

Project documentation is available in the `docs` directory.

- `docs/architecture.md` — System architecture and data flow
- `docs/features.md` — Project feature documentation

## 🚧 Development Status

The project is currently under active development.

### Completed

- Project structure
- Python virtual environment
- Backend foundation
- FastAPI application
- Basic health-check API
- Git and GitHub setup
- Initial system architecture
- Initial project documentation

### Planned

- Document upload and processing
- RAG pipeline implementation
- Embeddings generation
- Vector database integration
- AI provider integration
- Source citations
- Question Bank Generator
- PYQ analysis
- AI Quiz and Mock Tests
- AI Teacher
- Voice-based interaction
- Gamified learning
- Adaptive learning
- Progress analytics
- Offline-capable learning

Advanced features will be implemented progressively during later development phases.

## 🎯 Project Goal

The goal of Subject Guide AI is to transform a student's own academic materials into a personalized, source-grounded learning assistant.

Instead of searching through multiple documents, students can interact with their study material through AI-powered question answering, explanations, practice, and exam preparation.

## 📌 Current Version

Version: `0.1.0`

Status: Foundation Development