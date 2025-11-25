---
inclusion: always
---

# Project Structure

## Root Layout

```
/
├── agents/          # CrewAI agent implementations
├── tools/           # Utility tools (parsers, database, email, validators)
├── utils/           # Helper modules (config, logging, bulk processing, reports)
├── templates/       # HTML email templates
├── data/            # Runtime data storage
├── Chatbot/         # React frontend applications
├── app.py           # Main Streamlit application entry point
├── crew_setup.py    # Agent initialization and orchestration
└── requirements.txt # Python dependencies
```

## Key Directories

### `/agents`
AI agent implementations using CrewAI framework. Each agent has a specific role:
- `resume_matcher_agent.py` - Matches resumes with JD (primary agent)
- `resume_analyzer_agent.py` - Parses and analyzes resume content
- `jd_analyzer_agent.py` - Analyzes job descriptions
- `insight_extractor_agent.py` - Extracts candidate insights and scoring

### `/tools`
Reusable tools for data processing:
- `resume_parser_tool.py` - Multi-format resume text extraction
- `jd_parser_tool.py` - Job description parsing
- `database_tool.py` - SQLite database operations
- `email_tool.py` - Email generation and sending
- `validators.py` - Input validation utilities

### `/utils`
Helper modules:
- `bulk_processor.py` - Batch resume processing
- `report_generator.py` - Export results to CSV/JSON
- `logger_util.py` - Logging configuration
- `config.py` - Application configuration
- `helpers.py` - General utility functions

### `/data`
Runtime storage (not version controlled):
- `database.sqlite` - SQLite database file
- `uploads/` - Temporary uploaded resume files
- `results/` - Generated reports and exports

### `/Chatbot`
React frontend applications (multiple instances):
- `chatbot-app/` - Main chatbot interface
- `my-chatbot/` - Alternative chatbot implementation
- Standard Create React App structure with `src/`, `public/`

### `/templates`
HTML templates for email generation:
- `email_template.html` - General candidate emails
- `shortlist_email.html` - Shortlist notification emails

## Coding Conventions

### Python
- Agent classes follow CrewAI patterns with `role`, `goal`, `backstory`
- Database operations use context managers (`with self.conn:`)
- Error handling with try/except blocks and fallback mechanisms
- JSON parsing with regex fallback for LLM responses
- Session state management in Streamlit (`st.session_state`)

### File Handling
- Multiple fallback methods for resume parsing (PyPDF2 → pdfplumber → pdfminer)
- Always check file type before processing
- Create directories with `os.makedirs(exist_ok=True)`

### Agent Responses
- Expect JSON format from LLM agents
- Use regex to extract JSON if direct parsing fails
- Include status field in responses (`"status": "success"` or `"error"`)

### UI Patterns
- Streamlit containers with `border=True` for visual grouping
- Progress bars for batch operations
- Color-coded match levels with emojis (🟢🟡🟠🔴)
- Session state for multi-step workflows
