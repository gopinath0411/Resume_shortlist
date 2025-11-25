# AI-Powered Resume Analysis System
## Complete 2-Agent Workflow Implementation

### System Overview

This system implements the complete workflow from your document with:
- **Agent 1: Resume Analyzer** - Parses resumes and extracts structured data
- **Agent 2: Insight Extractor** - Analyzes candidates and computes confidence scores
- **ChromaDB** - Vector database for semantic search
- **Company SMTP** - Email integration
- **Streamlit Dashboard** - Real-time analytics

### Workflow Steps

1. **Upload Resume** → User uploads PDF/DOCX/TXT via Streamlit
2. **Agent 1: Parse Resume** → Extracts name, email, phone, skills, experience, education
3. **Agent 2: Analyze & Score** → Computes confidence score (0-100), identifies strengths/gaps
4. **Save to ChromaDB** → Stores candidate data with vector embeddings
5. **Dashboard Update** → Real-time metrics and charts
6. **Send Email** → Personalized emails via company SMTP
7. **Track & Report** → Export CSV/PDF reports

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the new application
streamlit run app_new.py
```

### Key Files

- `app_new.py` - Main Streamlit application (NEW - use this)
- `crew_setup.py` - Orchestrates 2-agent workflow
- `agents/resume_analyzer_agent.py` - Agent 1: Resume Parser
- `agents/insight_extractor_agent.py` - Agent 2: Insight Extractor
- `tools/chroma_database_tool.py` - ChromaDB vector database
- `tools/email_tool.py` - SMTP email integration
- `.env` - Configuration (API keys, SMTP settings)

### Configuration (.env)

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

### Features

✅ **Pure AI Analysis** - No hardcoded skills/experience fields
✅ **2-Agent Workflow** - Resume Parser → Insight Extractor
✅ **ChromaDB Vector Storage** - Semantic search capability
✅ **Company SMTP Integration** - Professional email delivery
✅ **Real-time Dashboard** - Analytics and metrics
✅ **Confidence Scoring** - 0-100 score based on job requirements
✅ **Automated Shortlisting** - Threshold-based filtering
✅ **Email Generation** - AI-generated personalized emails
✅ **Export Reports** - CSV download for all candidates

### Usage

1. **Configure .env** - Add your OpenRouter API key and SMTP settings
2. **Run application**: `streamlit run app_new.py`
3. **Upload resume** - PDF, DOCX, or TXT format
4. **AI analyzes** - 2 agents process the resume automatically
5. **Review results** - See confidence score, strengths, gaps
6. **Send email** - Personalized email to candidate
7. **Track progress** - View all candidates and shortlisted

### Differences from Old System

**OLD (app.py):**
- Manual JD entry with hardcoded fields
- Single agent matching
- SQLite database
- Basic matching logic

**NEW (app_new.py):**
- AI-driven analysis (no hardcoded fields)
- 2-agent workflow (Parser + Analyzer)
- ChromaDB vector database
- Semantic search capability
- Complete email workflow
- Better insights and scoring

### Next Steps

1. Install ChromaDB: `pip install chromadb sentence-transformers`
2. Test SMTP connection in sidebar
3. Upload a test resume
4. Review AI analysis results
5. Send test email to candidate

### Support

For issues:
- Check `.env` configuration
- Verify OpenRouter API key is valid
- Test SMTP connection before sending emails
- Ensure resume files are readable (not encrypted PDFs)
