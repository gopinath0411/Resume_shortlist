---
inclusion: always
---

# Product Overview

Resume Shortlisting System - An AI-powered recruitment tool that matches candidate resumes against job descriptions using LLM-based analysis.

## Core Features

- Manual job description entry with structured fields (title, skills, experience, education, mandatory requirements)
- Multi-format resume upload (PDF, DOCX, TXT) with fallback extraction methods
- AI-powered resume matching using CrewAI agents and OpenAI GPT-4o-mini
- Match scoring with categorization (Excellent 80%+, Good 60-79%, Moderate 40-59%, Poor <40%)
- Candidate shortlisting with CSV/JSON export
- SQLite database for candidate and analysis storage
- React-based chatbot interface (in development)

## User Flow

1. Enter job description details manually
2. Upload candidate resumes (multiple files supported)
3. System analyzes and scores each resume against JD
4. Review results by match category
5. Shortlist candidates and export results
