# Clean Project Structure

## Core Files (NEW SYSTEM)

```
resume-analysis-system/
├── app.py                              # Main Streamlit application
├── crew_setup.py                       # 2-Agent workflow orchestration
├── requirements.txt                    # Python dependencies
├── .env                                # Configuration (API keys, SMTP)
├── README_NEW_SYSTEM.md               # Documentation
│
├── agents/                             # AI Agents
│   ├── resume_analyzer_agent.py       # Agent 1: Resume Parser
│   ├── insight_extractor_agent.py     # Agent 2: Insight Extractor
│   └── __init__.py
│
├── tools/                              # Utility Tools
│   ├── chroma_database_tool.py        # ChromaDB vector database
│   └── email_tool.py                  # SMTP email integration
│
├── data/                               # Runtime Data
│   ├── uploads/                       # Uploaded resumes
│   ├── results/                       # Analysis results
│   └── chromadb/                      # ChromaDB storage (auto-created)
│
└── templates/                          # Email Templates
    ├── email_template.html
    └── shortlist_email.html
```

## Removed Files (Old System)

✅ Deleted:
- `agents/resume_matcher_agent.py` - Replaced by 2-agent system
- `agents/jd_analyzer_agent.py` - No longer needed
- `tools/database_tool.py` - Replaced by ChromaDB
- `tools/resume_parser_tool.py` - Parsing done by AI agent
- `tools/jd_parser_tool.py` - Not needed
- `tools/validators.py` - Validation by AI
- `utils/config.py` - Config in .env
- `utils/helpers.py` - Not needed
- `utils/report_generator.py` - Reports in app.py
- `utils/bulk_processor.py` - Not needed
- `utils/logger_util.py` - Not needed
- `data/database.sqlite` - Replaced by ChromaDB
- `install_dependencies.py` - Not needed

## Key Components

### 1. app.py
- Main Streamlit dashboard
- 4 tabs: Analyze Resume, All Candidates, Shortlisted, Send Emails
- Real-time statistics and charts
- File upload and text extraction
- Email sending interface

### 2. crew_setup.py
- Orchestrates 2-agent workflow
- Agent 1 → Agent 2 pipeline
- Error handling and result combination

### 3. agents/resume_analyzer_agent.py
- Agent 1: Resume Parser
- Extracts: name, email, phone, skills, experience, education
- Returns structured JSON

### 4. agents/insight_extractor_agent.py
- Agent 2: Insight Extractor
- Analyzes against job requirements
- Computes confidence score (0-100)
- Identifies strengths and gaps
- Generates personalized email

### 5. tools/chroma_database_tool.py
- ChromaDB vector database
- Stores candidates with embeddings
- Semantic search capability
- Statistics and reporting

### 6. tools/email_tool.py
- SMTP email integration
- Company mail server support
- HTML email formatting
- Connection testing

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## Configuration (.env)

```env
# LLM API
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct

# SMTP Email
SMTP_SERVER=mail.yourcompany.com
SMTP_PORT=587
SENDER_EMAIL=your.email@company.com
SENDER_PASSWORD=your_password
COMPANY_NAME=Your Company Name

# Job Requirements
JOB_TITLE=Senior Python Developer
REQUIRED_SKILLS=Python,Django,FastAPI,PostgreSQL,AWS
REQUIRED_EXPERIENCE_YEARS=3
```

## Workflow

1. **Upload Resume** → PDF/DOCX/TXT via Streamlit
2. **Extract Text** → PyPDF2/pdfplumber/python-docx
3. **Agent 1: Parse** → Extract structured data
4. **Agent 2: Analyze** → Score and generate insights
5. **Save to ChromaDB** → Vector storage with embeddings
6. **Display Results** → Dashboard with metrics
7. **Send Email** → Personalized email via SMTP
8. **Track & Report** → Export CSV/PDF

## Clean & Minimal

The new system is:
- ✅ Cleaner - Only essential files
- ✅ AI-driven - No hardcoded logic
- ✅ Modular - Clear separation of concerns
- ✅ Scalable - ChromaDB vector storage
- ✅ Production-ready - Complete workflow
