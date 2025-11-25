---
inclusion: always
---

# Tech Stack

## Backend (Python)

- **Framework**: Streamlit (web UI)
- **AI/LLM**: CrewAI, LangChain, OpenAI GPT-4o-mini
- **Resume Parsing**: PyPDF2, pdfplumber, pdfminer, python-docx, pyresparser
- **Database**: SQLite with SQLAlchemy
- **Data Processing**: pandas
- **Environment**: python-dotenv

## Frontend (React)

- **Framework**: React 19.2.0
- **Build Tool**: react-scripts (Create React App)
- **Styling**: Tailwind CSS 4.1.17
- **Icons**: lucide-react
- **Testing**: Jest, React Testing Library

## Common Commands

### Python Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py

# Run with virtual environment
.venv\Scripts\activate  # Windows
python app.py
```

### React Frontend

```bash
# Navigate to chatbot directory
cd Chatbot/chatbot-app

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm build

# Run tests
npm test
```

## Environment Setup

- Requires `.env` file with OpenAI API key
- Python virtual environment recommended (`.venv` or `venv`)
- Node.js required for React frontend

## AI Agent Architecture

- Uses CrewAI framework for agent orchestration
- Agents are stateless and task-focused
- LLM responses parsed as JSON for structured output
- Temperature set to 0 for consistent matching results
