"""
Agent 1: Resume Analyzer - Parses and extracts structured data from resumes
"""
import json
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_key_manager import get_api_key_manager

load_dotenv()
logger = logging.getLogger(__name__)


def parse_resume_with_agent(resume_text: str, max_retries: int = 3) -> dict:
    """Parse resume using direct API call with automatic key rotation on rate limit"""
    
    api_manager = get_api_key_manager()
    provider = os.getenv("LLM_PROVIDER", "openrouter").lower()
    
    if provider == "groq":
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        base_url = "https://api.groq.com/openai/v1"
    else:
        model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-70b-instruct")
        base_url = "https://openrouter.ai/api/v1"
    
    # Try with rotation
    for attempt in range(max_retries):
        try:
            api_key = api_manager.get_current_key()
            logger.info(f"Using {provider.upper()} API Key #{api_manager.get_key_number()}/{api_manager.get_total_keys()}")
            
            if not api_key or api_key == "your_groq_key_here":
                return {"status": "error", "error": f"{provider.upper()} API key not configured"}
        
            logger.info(f"Using model: {model}")
            
            # Use OpenAI client
            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            prompt = f"""You are an expert resume parser. Extract information EXACTLY as written in the resume.

RESUME TEXT:
{resume_text[:4000]}

CRITICAL INSTRUCTIONS - READ CAREFULLY:

1. SKILLS EXTRACTION - MOST IMPORTANT:
   ⚠️ Extract ONLY skills that are EXPLICITLY MENTIONED in the resume text
   ⚠️ DO NOT add any skills that are not written in the resume
   ⚠️ DO NOT infer or assume skills
   ⚠️ DO NOT add related skills that aren't mentioned
   ⚠️ Copy the exact skill names as they appear in the resume
   
   Look for skills in:
   - Skills section
   - Technical skills section
   - Job descriptions
   - Project descriptions
   
   If a skill is NOT written in the resume, DO NOT include it!

2. EXPERIENCE CALCULATION:
   - Count ONLY full-time work experience (NOT internships or education)
   - Calculate ACCURATELY from the dates mentioned in the resume
   - If dates show "Oct 2023 - July 2025", that's approximately 2 years (or 1.75 years)
   - Round to nearest whole number or use decimal (e.g., 1.75, 2)
   - If fresher with no full-time work, set experience_years to 0
   - Add up all full-time work periods accurately

3. CONTACT EXTRACTION:
   - Extract name, email, phone number exactly as written

EXAMPLE:
If resume says: "Skills: Python, SQL, Active Directory, DNS"
Then extract: ["Python", "SQL", "Active Directory", "DNS"]

DO NOT extract: ["Python", "SQL", "Active Directory", "DNS", "Windows", "Linux", "Networking"]
(because Windows, Linux, Networking are NOT mentioned)

Return ONLY valid JSON with this structure:
{{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1234567890",
    "skills": ["Only", "Skills", "Actually", "Written", "In", "Resume"],
    "experience_years": 2,
    "experience_details": [
        {{"role": "Job Title", "company": "Company Name", "duration": "2 years", "type": "full-time"}}
    ],
    "education": [
        {{"degree": "Degree Name", "field": "Field", "year": 2020}}
    ],
    "summary": "Brief summary"
}}

⚠️ CRITICAL: Only extract skills that are ACTUALLY WRITTEN in the resume text above. Do not add anything extra!

Return ONLY the JSON, no additional text."""
        
            logger.info("Calling API for resume parsing...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert resume parser. Read carefully and extract ALL skills, experience, and contact information. Return ONLY valid JSON with comprehensive skill lists."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            logger.info(f"Received response: {len(result_text)} characters")
            
            # Parse JSON response
            try:
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    parsed_data["status"] = "success"
                    logger.info("✅ Successfully parsed JSON response")
                    return parsed_data
                else:
                    logger.error("No JSON found in response")
                    return {"status": "error", "error": "Could not extract JSON from response"}
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                return {"status": "error", "error": f"JSON parsing failed: {str(e)}", "raw_response": result_text[:500]}
        
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a rate limit error
            if "rate_limit" in error_str.lower() or "429" in error_str:
                logger.warning(f"⚠️ Rate limit hit on Key #{api_manager.get_key_number()}")
                
                # Rotate to next key
                if attempt < max_retries - 1:
                    api_manager.rotate_to_next()
                    logger.info(f"🔄 Retrying with Key #{api_manager.get_key_number()}...")
                    continue
                else:
                    logger.error("❌ All API keys exhausted, all hit rate limits")
                    return {"status": "error", "error": "All API keys have hit rate limits. Please wait or add more keys."}
            else:
                # Non-rate-limit error, don't retry
                logger.error(f"API call failed: {error_str}")
                return {"status": "error", "error": f"API call failed: {error_str}"}
    
    return {"status": "error", "error": "Failed after all retries"}
