

"""
Agent 2: Insight Extractor - Analyzes resume against job requirements and scores candidates
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


def analyze_candidate_with_agent(parsed_resume: dict, job_requirements: dict, max_retries: int = 3) -> dict:
    """Analyze candidate using direct API call with automatic key rotation"""
    
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
            
            prompt = f"""You are an expert recruiter analyzing a candidate against job requirements.

CANDIDATE DATA:
{json.dumps(parsed_resume, indent=2)}

JOB REQUIREMENTS:
- Job Title: {job_requirements.get('job_title', 'N/A')}
- Required Skills: {job_requirements.get('required_skills', 'N/A')}
- Required Experience: {job_requirements.get('required_experience_years', '0 to 3')} years
- Technical Skills: {job_requirements.get('nice_to_have', 'N/A')}

CRITICAL ANALYSIS INSTRUCTIONS:

1. KEY STRENGTHS (3-5 items):
   - List SPECIFIC skills from candidate that MATCH job requirements
   - Example: "Strong experience in Python and SQL" NOT just "Good technical skills"
   - Mention actual technologies/tools they know
   - Include relevant experience level

2. GAPS (2-4 items):
   - List SPECIFIC required skills the candidate is MISSING
   - Example: "No experience with AWS" NOT just "Lacks cloud skills"
   - Mention specific technologies from job requirements they don't have
   - Note experience gaps if applicable

3. RECOMMENDATION:
   - Write 2-3 sentences explaining the match
   - Mention specific skills that align or are missing
   - Be honest about fit level

4. CONFIDENCE SCORE (0-100):
   - Skill match: 40% (how many required skills they have)
   - Experience level: 30% (years match requirements)
   - Education: 20% (relevant degree)
   - Achievements: 10%

Return ONLY valid JSON with this structure:
{{
    "candidate_name": "Name",
    "candidate_email": "email@example.com",
    "confidence_score": 75,
    "shortlisted": true,
    "key_strengths": [
        "Proficient in Python with 2+ years experience",
        "Strong SQL and database management skills",
        "Experience with data analysis and Excel"
    ],
    "gaps": [
        "No experience with AWS cloud platform",
        "Missing Docker/Kubernetes knowledge",
        "Limited experience (0 years vs 2-3 required)"
    ],
    "recommendation": "Candidate shows strong foundational skills in Python and SQL which align with core requirements. However, lacks cloud experience (AWS) and containerization skills. Consider for junior role or with training.",
    "email_subject": "Interview Opportunity - Job Title",
    "email_body": "<p>Dear Candidate...</p>"
}}

Return ONLY the JSON, no additional text."""
        
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert recruiter. Analyze candidates and return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    analysis_data["status"] = "success"
                    logger.info("✅ Successfully analyzed candidate")
                    return analysis_data
                else:
                    return {"status": "error", "error": "Could not extract JSON from response"}
            except json.JSONDecodeError as e:
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
