# Subject Guide AI — System Architecture

## 1. High-Level Architecture

Subject Guide AI is an AI-powered educational assistant that allows students to upload notes, textbooks, and previous-year question papers and ask questions based on their academic materials.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from uploaded documents before generating an answer.

### High-Level Flow

    Student
       |
       v
    Upload Notes / Textbooks / PYQs
       |
       v
    Document Storage
       |
       v
    Document Processing
       |
       v
    Text Extraction & Chunking
       |
       v
    Embeddings Generation
       |
       v
    Vector Database
       |
       v
    Student Question
       |
       v
    Question Embedding
       |
       v
    Semantic Search
       |
       v
    Relevant Document Chunks
       |
       v
    AI Model
    (Gemini / Ollama + Qwen3)
       |
       v
    Grounded Answer + Source Citation

## 2. Main Components

The system is divided into several major components.

### 2.1 Frontend

The frontend provides the student-facing interface.

Main responsibilities:

- Student interaction
- Document upload
- Question input
- AI answer display
- Source citation display
- Quiz interface
- Question bank interface
- Progress tracking
- Gamified learning interface
- Voice interaction interface

The frontend communicates with the backend through REST APIs.

### 2.2 Backend

The backend is responsible for application logic and API management.

Main responsibilities:

- API request handling
- Authentication and authorization
- Document processing
- RAG pipeline management
- AI provider selection
- Question answering
- Quiz generation
- Question bank generation
- PYQ analysis
- Progress management
- Study planning
- Analytics

The backend is implemented using FastAPI.

### 2.3 Document Processing Layer

The document processing layer handles uploaded academic materials.

Supported materials may include:

- PDF
- Text documents
- Notes
- Textbooks
- Previous-year question papers
- Other supported academic documents

Processing steps:

    Uploaded Document
           |
           v
    File Validation
           |
           v
    Text Extraction
           |
           v
    Text Cleaning
           |
           v
    Document Chunking
           |
           v
    Metadata Generation
           |
           v
    Embedding Generation
           |
           v
    Vector Storage

### 2.4 Vector Database

The vector database stores embeddings generated from academic documents.

Possible vector database options:

- Pinecone
- Supabase Vector Store
- Other compatible vector databases

Each stored vector should contain relevant metadata such as:

- Document name
- Page number
- Subject
- Unit
- Topic
- Chunk identifier

This metadata helps the system provide source-grounded answers and citations.

### 2.5 AI Layer

The AI layer generates answers using retrieved academic information.

Supported AI providers:

    AI Provider
         |
         +-------------------+
         |                   |
         v                   v
      Gemini           Ollama + Qwen3
     Cloud AI             Local AI

Gemini can be used for cloud-based AI processing.

Ollama with Qwen3 can be used for local AI processing and offline-capable scenarios.

The system can select the AI provider based on configuration.

## 3. Core RAG Flow

Retrieval-Augmented Generation is the core intelligence layer of Subject Guide AI.

### RAG Pipeline

    Academic Documents
           |
           v
    Text Extraction
           |
           v
    Text Chunking
           |
           v
    Embeddings
           |
           v
    Vector Database
           |
           +----------------------+
                                  |
    Student Question             |
           |                      |
           v                      |
    Question Embedding            |
           |                      |
           v                      |
    Semantic Search --------------+
           |
           v
    Top Relevant Chunks
           |
           v
    Context Construction
           |
           v
    AI Model
           |
           v
    Grounded Answer
           |
           v
    Source Citation

### RAG Process

1. Student uploads academic materials.
2. Documents are processed and converted into text.
3. Text is divided into smaller chunks.
4. Each chunk is converted into an embedding.
5. Embeddings are stored in the vector database.
6. Student submits a question.
7. The question is converted into an embedding.
8. The system performs semantic similarity search.
9. Relevant chunks are retrieved.
10. Retrieved content is provided to the AI model as context.
11. AI generates an answer using the retrieved information.
12. The system returns the answer with source information.

### Grounded Response Principle

The AI should prioritize the student's uploaded academic material.

When sufficient information is not available in the provided material, the system should clearly indicate that the information could not be found in the uploaded sources instead of confidently generating unsupported information.

## 4. AI Provider Architecture

Subject Guide AI supports multiple AI providers.

### Cloud AI — Gemini

Gemini can provide:

- Advanced question answering
- Document understanding
- Question generation
- Quiz generation
- PYQ analysis
- AI Teacher functionality
- Summarization
- Multilingual responses
- Advanced reasoning

### Local AI — Ollama + Qwen3

Ollama provides a local model runtime.

Qwen3 can be used as the local language model.

Local AI can provide:

- Local question answering
- Privacy-focused processing
- Low-connectivity learning
- Offline-capable learning scenarios
- Reduced dependency on cloud APIs

### Provider Switching

The application can use an environment variable to select the AI provider.

Example:

    AI_PROVIDER=gemini

or:

    AI_PROVIDER=ollama

This allows the application architecture to remain flexible.

## 5. Future Extensions

The architecture is designed to support additional educational features.

### 5.1 AI Subject Guide

The AI can explain:

- Subjects
- Units
- Topics
- Concepts
- Definitions
- Examples

The explanations can be adapted to the student's learning level.

### 5.2 Question Bank Generator

The system can generate questions from uploaded academic material.

Possible question types:

- Multiple Choice Questions
- Short Answer Questions
- Long Answer Questions
- 2-mark questions
- 5-mark questions
- 10-mark questions
- Practice questions
- Revision questions

### 5.3 Previous-Year Question Analysis

The system can analyze previous-year question papers to identify:

- Frequently asked topics
- Repeated questions
- Important units
- Question patterns
- Possible high-priority topics
- Marks distribution

### 5.4 AI Quiz and Mock Test

The system can generate quizzes and mock tests based on:

- Subject
- Unit
- Topic
- Difficulty
- Previous performance
- Exam pattern

### 5.5 Adaptive Learning

The system can identify weak topics based on student performance.

Example:

    Learn
      |
      v
    Practice
      |
      v
    Quiz
      |
      v
    Evaluate
      |
      v
    Weak Topic Detection
      |
      v
    Additional Practice
      |
      v
    Re-evaluation
      |
      v
    Level Up

## 6. Component Data Flow

The major system components communicate through the following flow:

                        STUDENT
                           |
                           v
                  +----------------+
                  |    Frontend    |
                  +----------------+
                           |
                           v
                  +----------------+
                  |    FastAPI     |
                  |    Backend     |
                  +----------------+
                           |
             +-------------+-------------+
             |                           |
             v                           v
    +-------------------+       +-------------------+
    | Document Service  |       | Question Service  |
    +-------------------+       +-------------------+
             |                           |
             v                           v
    +-------------------+       +-------------------+
    | Document Storage  |       |   RAG Pipeline    |
    +-------------------+       +-------------------+
                                         |
                                         v
                               +-------------------+
                               |  Vector Database  |
                               +-------------------+
                                         |
                                         v
                               +-------------------+
                               |   AI Provider     |
                               +-------------------+
                                  |           |
                                  v           v
                               Gemini     Ollama/Qwen3
                                  |           |
                                  +-----+-----+
                                        |
                                        v
                                   AI Response
                                        |
                                        v
                                     Student

## 7. API Layer

The backend exposes REST APIs for communication between the frontend and backend.

### Initial API Endpoints

GET /

Returns basic backend status.

GET /health

Returns backend health status.

### Future API Endpoints

Document APIs:

- POST /documents/upload
- GET /documents
- GET /documents/{document_id}
- DELETE /documents/{document_id}

Question APIs:

- POST /questions/ask
- POST /questions/explain

Question bank APIs:

- POST /question-bank/generate
- GET /question-bank

Quiz APIs:

- POST /quiz/generate
- POST /quiz/submit
- GET /quiz/results

Progress APIs:

- GET /progress
- POST /progress/update

Voice APIs:

- POST /voice/question
- POST /voice/response

These endpoints are planned extensions and may be implemented progressively.

## 8. AI Provider and RAG Layer

The AI provider layer separates the application logic from individual AI models.

### Provider Abstraction

                 Application
                      |
                      v
              AI Provider Layer
                      |
            +---------+---------+
            |                   |
            v                   v
         Gemini          Ollama / Qwen3

This architecture makes it possible to change the AI model without redesigning the entire application.

### RAG + AI Provider

    Student Question
           |
           v
    RAG Retrieval
           |
           v
    Relevant Academic Context
           |
           v
    AI Provider
       |          |
       v          v
    Gemini    Ollama/Qwen3
       |          |
       +----+-----+
            |
            v
    Grounded Response

## 9. Database and Storage Architecture

The system may use multiple storage layers.

### 9.1 Document Storage

Uploaded academic files can be stored using:

- Google Drive
- Cloud storage
- Local storage
- Object storage

The exact storage provider can be selected based on deployment requirements.

### 9.2 Vector Storage

The vector database stores:

    Document Chunk
          |
          +-- Embedding
          |
          +-- Document ID
          |
          +-- Page Number
          |
          +-- Subject
          |
          +-- Unit
          |
          +-- Topic

### 9.3 Application Database

A relational or document database may be used for application-level data such as:

- Student profiles
- Uploaded document metadata
- Questions
- Quiz results
- Progress
- Study plans
- Rewards
- Analytics

Possible database options include:

- PostgreSQL
- SQLite for development
- Supabase

## 10. Security and Configuration Architecture

Security is an important part of the application architecture.

### Environment Variables

Sensitive configuration should not be stored directly in source code.

Examples:

    GEMINI_API_KEY
    OLLAMA_BASE_URL
    OLLAMA_MODEL
    DATABASE_URL

These values should be stored in environment variables.

The `.env` file should never be committed to GitHub.

The repository should only contain:

    .env.example

### API Security

Future production implementation may include:

- Authentication
- Authorization
- Secure API endpoints
- Input validation
- File validation
- File size limits
- Rate limiting
- API key protection
- Secure database access

### Document Security

Uploaded academic documents should be handled securely.

The system should:

- Validate uploaded files
- Restrict unsupported file types
- Limit file size
- Avoid exposing private documents
- Protect student data
- Prevent unauthorized access

### AI Safety and Grounding

The AI response layer should prioritize retrieved academic content.

The system should:

- Retrieve relevant document chunks
- Provide source information
- Avoid unsupported claims
- Clearly communicate when information is unavailable
- Reduce hallucination through source-grounded generation

### Configuration Flow

    Environment Variables
            |
            v
    Application Configuration
            |
            +-------------------+
            |                   |
            v                   v
       AI Provider         Database / Storage
            |
            v
      Gemini or Ollama/Qwen3

## 11. Overall System Architecture

The complete architecture can be summarized as:

                         STUDENT
                            |
                            v
                    +---------------+
                    |   Frontend    |
                    +---------------+
                            |
                            v
                    +---------------+
                    |    FastAPI    |
                    |    Backend    |
                    +---------------+
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
   Document Service   Question Service   User/Progress
          |                 |                 |
          v                 v                 v
   Document Storage    RAG Pipeline      Application DB
                            |
                            v
                    +---------------+
                    | Vector Store  |
                    +---------------+
                            |
                            v
                    Relevant Context
                            |
                            v
                    +---------------+
                    | AI Provider   |
                    +---------------+
                      |           |
                      v           v
                   Gemini    Ollama/Qwen3
                      |           |
                      +-----+-----+
                            |
                            v
                    Grounded Answer
                            |
                            v
                         STUDENT

## 12. Architecture Goals

The architecture is designed around the following goals:

- Source-grounded academic answers
- Modular backend design
- Flexible AI provider support
- Scalable RAG architecture
- Secure document handling
- Student-focused learning experience
- Support for future AI educational features
- Cloud and local AI flexibility
- Maintainable and testable codebase
- Future-ready architecture for production deployment

**Current Architecture Status:** Foundation architecture completed. Advanced RAG, vector database, AI provider integration, authentication, analytics, voice features, and other advanced capabilities will be implemented progressively during later development phases.