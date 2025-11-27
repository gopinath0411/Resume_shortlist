"""
Resume Filter Page - Extract all content from resumes and export to Excel
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.resume_analyzer_agent import parse_resume_with_agent
from utils.api_key_manager import get_api_key_manager

# Try to import PDF/DOCX libraries
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


def extract_text_from_file(uploaded_file):
    """Extract text from PDF/DOCX/TXT files"""
    try:
        if uploaded_file.type == "application/pdf":
            # Try PyPDF2 first
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
                if text.strip():
                    return text, True, None
            except:
                pass
            
            # Fallback to pdfplumber
            try:
                uploaded_file.seek(0)
                with pdfplumber.open(uploaded_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                if text.strip():
                    return text, True, None
            except:
                pass
            
            return "", False, "Could not extract text from PDF"
        
        elif "wordprocessingml" in uploaded_file.type or uploaded_file.name.endswith(".docx"):
            try:
                doc = Document(uploaded_file)
                text = "\n".join([para.text for para in doc.paragraphs])
                if text.strip():
                    return text, True, None
                return "", False, "DOCX file is empty"
            except Exception as e:
                return "", False, f"Error reading DOCX: {str(e)}"
        
        else:  # Text file
            try:
                text = uploaded_file.getvalue().decode("utf-8")
                if text.strip():
                    return text, True, None
                return "", False, "Text file is empty"
            except Exception as e:
                return "", False, f"Error reading text file: {str(e)}"
    
    except Exception as e:
        return "", False, f"Unexpected error: {str(e)}"


# Page config
st.set_page_config(page_title="Resume Filter", layout="wide", page_icon="🔍")

# Title
st.title("🔍 Resume Filter")
st.markdown("**Extract all information from resumes and export to Excel**")

# Check API keys
try:
    api_mgr = get_api_key_manager()
    if api_mgr.get_total_keys() > 0:
        st.success(f"✅ {api_mgr.get_total_keys()} API key(s) loaded")
    else:
        st.error("❌ No API keys loaded!")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")

st.markdown("---")

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = []

# File uploader
st.header("📤 Upload Resumes")
uploaded_files = st.file_uploader(
    "Upload multiple resumes to extract information",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    help="Upload PDF, DOCX, or TXT files"
)

if uploaded_files:
    st.info(f"📊 **{len(uploaded_files)} resume(s) selected**")
    
    if st.button("🚀 Extract Information", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        extracted_data = []
        successful = 0
        failed = 0
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
            
            # Extract text
            resume_text, success, error = extract_text_from_file(uploaded_file)
            
            if not success:
                st.error(f"❌ {uploaded_file.name}: {error}")
                failed += 1
                progress_bar.progress((idx + 1) / len(uploaded_files))
                continue
            
            # Parse with agent
            try:
                result = parse_resume_with_agent(resume_text)
                
                if result.get("status") == "success":
                    # Extract all data
                    data = {
                        "File Name": uploaded_file.name,
                        "Name": result.get("name", "N/A"),
                        "Email": result.get("email", "N/A"),
                        "Phone": result.get("phone", "N/A"),
                        "Experience (Years)": result.get("experience_years", 0),
                        "Skills": ", ".join(result.get("skills", [])),
                        "Education": ", ".join([f"{edu.get('degree', '')} in {edu.get('field', '')}" for edu in result.get("education", [])]),
                        "Summary": result.get("summary", "N/A"),
                        "Extracted Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    extracted_data.append(data)
                    successful += 1
                    st.success(f"✅ {uploaded_file.name} - Extracted successfully")
                else:
                    st.error(f"❌ {uploaded_file.name}: {result.get('error', 'Unknown error')}")
                    failed += 1
                    
            except Exception as e:
                st.error(f"❌ {uploaded_file.name}: {str(e)}")
                failed += 1
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        # Save to session state
        st.session_state.extracted_data = extracted_data
        
        # Final summary
        progress_bar.progress(1.0)
        status_text.success("✅ Extraction complete!")
        
        st.success(f"""
        **Extraction Summary:**
        - ✅ Successful: {successful}
        - ❌ Failed: {failed}
        - 📊 Total: {len(uploaded_files)}
        """)

# Display extracted data
if st.session_state.extracted_data:
    st.markdown("---")
    st.header("📋 Extracted Information")
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.extracted_data)
    
    # Display table
    st.dataframe(df, use_container_width=True, height=400)
    
    # Download buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Excel download
        excel_file = f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(excel_file, index=False, engine='openpyxl')
        
        with open(excel_file, 'rb') as f:
            st.download_button(
                "📥 Download Excel",
                f.read(),
                excel_file,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # Clean up temp file
        if os.path.exists(excel_file):
            os.remove(excel_file)
    
    with col2:
        # CSV download
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col3:
        # Clear data
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.extracted_data = []
            st.rerun()
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Resumes", len(df))
    
    with col2:
        avg_exp = df["Experience (Years)"].mean()
        st.metric("Avg Experience", f"{avg_exp:.1f} years")
    
    with col3:
        total_skills = sum([len(skills.split(", ")) for skills in df["Skills"] if skills != "N/A"])
        st.metric("Total Skills", total_skills)
    
    with col4:
        with_email = len(df[df["Email"] != "N/A"])
        st.metric("With Email", with_email)

else:
    st.info("👆 Upload resumes above to extract information")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🔍 Resume Filter | Powered by AI Agent + Groq Llama</p>
</div>
""", unsafe_allow_html=True)
