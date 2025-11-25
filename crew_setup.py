"""
CrewAI Multi-Agent Setup - Orchestrates Resume Analysis Workflow
"""
from agents.resume_analyzer_agent import parse_resume_with_agent
from agents.insight_extractor_agent import analyze_candidate_with_agent


import logging

logger = logging.getLogger(__name__)


def run_complete_analysis(resume_text: str, job_requirements: dict) -> dict:
    """
    Execute complete 2-agent workflow:
    1. Agent 1: Parse resume and extract data
    2. Agent 2: Analyze and score candidate
    """
    
    # Step 1: Parse Resume (Agent 1)
    logger.info("=" * 60)
    logger.info("🤖 AGENT 1: Starting Resume Parsing")
    logger.info("=" * 60)
    logger.info(f"Resume length: {len(resume_text)} characters")
    
    parsed_resume = parse_resume_with_agent(resume_text)
    
    if parsed_resume.get("status") != "success":
        logger.error(f"❌ AGENT 1 FAILED: {parsed_resume.get('error')}")
        return {
            "status": "error",
            "error": f"Resume parsing failed: {parsed_resume.get('error', 'Unknown error')}",
            "stage": "parsing"
        }
    
    logger.info("✅ AGENT 1 SUCCESS: Resume parsed successfully")
    logger.info(f"Extracted name: {parsed_resume.get('name', 'N/A')}")
    logger.info(f"Extracted email: {parsed_resume.get('email', 'N/A')}")
    logger.info(f"Extracted skills: {len(parsed_resume.get('skills', []))} skills")
    
    # Step 2: Analyze & Score (Agent 2)
    logger.info("=" * 60)
    logger.info("🤖 AGENT 2: Starting Candidate Analysis")
    logger.info("=" * 60)
    logger.info(f"Job Title: {job_requirements.get('job_title')}")
    logger.info(f"Required Skills: {job_requirements.get('required_skills')}")
    
    analysis_result = analyze_candidate_with_agent(parsed_resume, job_requirements)
    
    if analysis_result.get("status") != "success":
        logger.error(f"❌ AGENT 2 FAILED: {analysis_result.get('error')}")
        return {
            "status": "error",
            "error": f"Analysis failed: {analysis_result.get('error', 'Unknown error')}",
            "stage": "analysis",
            "parsed_data": parsed_resume
        }
    
    logger.info("✅ AGENT 2 SUCCESS: Analysis completed")
    logger.info(f"Confidence Score: {analysis_result.get('confidence_score', 0)}%")
    logger.info(f"Recommendation: {analysis_result.get('recommendation', 'N/A')}")
    logger.info(f"Shortlisted: {analysis_result.get('shortlisted', False)}")
    
    # Combine results
    final_result = {
        "status": "success",
        "parsed_resume": parsed_resume,
        "analysis": analysis_result
    }
    
    logger.info("=" * 60)
    logger.info("✅ WORKFLOW COMPLETE")
    logger.info("=" * 60)
    
    return final_result
