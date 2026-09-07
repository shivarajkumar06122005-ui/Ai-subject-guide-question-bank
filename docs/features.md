# Subject Guide AI — Feature Specification

## 1. Core Features

### 1.1 Multi-Document Upload

Students can upload multiple academic materials such as:

- Notes
- Textbooks
- Previous-Year Question Papers
- Study documents

The uploaded materials are processed and prepared for semantic retrieval.

### 1.2 RAG-Based Question Answering

Students can ask questions about their uploaded study materials.

The RAG pipeline retrieves relevant academic content before generating the answer.

### 1.3 Source and Page Citations

AI responses should provide the source document and page information when available.

This helps students verify the generated answer against their original study material.

### 1.4 AI Subject Guide

The system acts as an interactive subject guide that explains concepts using the student's available academic materials.

### 1.5 Question Bank Generator

The system can generate practice questions from uploaded academic content.

Questions can be organized by:

- Subject
- Unit
- Chapter
- Difficulty
- Marks

### 1.6 Previous-Year Question Analysis

Previous-year question papers can be analyzed to identify:

- Frequently asked topics
- Important concepts
- Question patterns
- Repeated questions
- Topic-wise distribution

### 1.7 AI Quiz and Mock Test Generator

The system can generate quizzes and mock tests from the student's study materials.

### 1.8 Exam Mode

Answers can be generated according to examination requirements, including:

- 2-mark answers
- 5-mark answers
- 10-mark answers

### 1.9 Weak Topic Detection

The system can identify topics where a student performs poorly based on quiz and practice results.

### 1.10 Personalized Study Planner

The system can generate study recommendations based on:

- Student progress
- Weak topics
- Upcoming examinations
- Available study time

---

## 2. Advanced Features

### 2.1 AI Flashcards

Generate revision flashcards from academic materials.

### 2.2 AI Mind Maps

Convert important topics and relationships into visual mind maps.

### 2.3 Multilingual Support

Provide explanations and learning content in supported regional and international languages.

### 2.4 Image Question Solver

Allow students to submit an image containing an academic question and receive an explanation.

### 2.5 Voice-Based Question Answering

Students can ask academic questions using voice input.

### 2.6 Student Progress Dashboard

Display:

- Learning progress
- Quiz performance
- Completed topics
- Weak topics
- Study activity
- Learning streak

### 2.7 Faculty Analytics

Provide aggregated learning insights that can help faculty understand student performance and commonly difficult topics.

### 2.8 Dual AI Support

The system supports:

- Gemini for cloud-based AI
- Ollama + Qwen3 for local AI

### 2.9 n8n Automation

n8n can be used to automate workflows such as:

- Document ingestion
- Notifications
- Question logging
- AI processing workflows

### 2.10 Vector Database and Semantic Search

Academic document embeddings are stored in a vector database to enable semantic retrieval.

### 2.11 Hallucination Guard

The system prioritizes retrieved academic context and source citations when generating answers.

If sufficient supporting information is unavailable, the system should clearly indicate the limitation.

---

## 3. AI Teacher

The AI Teacher provides an interactive learning experience.

It can:

- Explain concepts step-by-step
- Answer follow-up questions
- Provide examples
- Generate practice questions
- Identify weak areas
- Recommend revision topics

The AI Teacher should adapt explanations according to the student's learning progress.

---

## 4. Adaptive Learning

The learning cycle is:

```text
Learn
  ↓
Practice
  ↓
Quiz
  ↓
Evaluate
  ↓
Detect Weakness
  ↓
Additional Practice
  ↓
Re-explain
  ↓
Level Up

Academic Concept
       ↓
AI Teacher Explanation
       ↓
Visual Representation
       ↓
Interactive Learning
       ↓
Practice / Quiz
       ↓
Progress Evaluation

                 Student
                    ↓
             AI Learning System
               /            \
              /              \
             ↓                ↓
       Online Mode        Local Mode
          Gemini        Ollama + Qwen3

Student Activity
       ↓
Performance Analysis
       ↓
Weak Topic Detection
       ↓
Personalized Recommendation
       ↓
Practice / Revision
       ↓
Progress Update