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
            
            # Parse with agent - Let agent extract ALL content dynamically
            try:
                result = parse_resume_with_agent(resume_text)
                
                if result.get("status") == "success":
                    # Agent extracts content dynamically - no predefined structure
                    # We take whatever the agent returns
                    data = {
                        "File Name": uploaded_file.name,
                        "Extracted Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Add all fields the agent extracted (dynamic)
                    for key, value in result.items():
                        if key == "status":
                            continue
                        
                        # Format the value for display
                        if isinstance(value, list):
                            if len(value) > 0 and isinstance(value[0], dict):
                                # List of dicts (like education, experience)
                                formatted = " | ".join([str(item) for item in value])
                                data[key.replace("_", " ").title()] = formatted
                            else:
                                # Simple list (like skills)
                                data[key.replace("_", " ").title()] = ", ".join(str(v) for v in value)
                        elif isinstance(value, dict):
                            # Dict - convert to string
                            data[key.replace("_", " ").title()] = str(value)
                        else:
                            # Simple value
                            data[key.replace("_", " ").title()] = value if value else "N/A"
                    
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
        # Word document download
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        doc.add_heading('Resume Extraction Report', 0)
        doc.add_paragraph(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        doc.add_paragraph(f'Total Resumes: {len(df)}')
        doc.add_paragraph('')
        
        # Add table
        table = doc.add_table(rows=1, cols=len(df.columns))
        table.style = 'Light Grid Accent 1'
        
        # Header row
        hdr_cells = table.rows[0].cells
        for i, column in enumerate(df.columns):
            hdr_cells[i].text = str(column)
        
        # Data rows
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, value in enumerate(row):
                row_cells[i].text = str(value)
        
        # Save to bytes
        from io import BytesIO
        doc_file = BytesIO()
        doc.save(doc_file)
        doc_file.seek(0)
        
        st.download_button(
            "📥 Download Word",
            doc_file.read(),
            f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    
    with col3:
        # Clear data
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.extracted_data = []
            st.rerun()
    
    # Statistics - Dynamic based on extracted data
    st.markdown("---")
    st.subheader("📊 Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Resumes", len(df))
    
    with col2:
        # Count resumes with email
        email_cols = [col for col in df.columns if 'email' in col.lower()]
        if email_cols:
            with_email = len(df[df[email_cols[0]] != "N/A"])
            st.metric("With Email", with_email)
        else:
            st.metric("Columns", len(df.columns))
    
    with col3:
        # Count resumes with phone
        phone_cols = [col for col in df.columns if 'phone' in col.lower()]
        if phone_cols:
            with_phone = len(df[df[phone_cols[0]] != "N/A"])
            st.metric("With Phone", with_phone)
        else:
            st.metric("Fields Extracted", len(df.columns) - 2)
    
    with col4:
        # Count resumes with skills
        skill_cols = [col for col in df.columns if 'skill' in col.lower()]
        if skill_cols:
            with_skills = len(df[df[skill_cols[0]] != "N/A"])
            st.metric("With Skills", with_skills)
        else:
            st.metric("Data Points", len(df) * len(df.columns))

else:
    st.info("👆 Upload resumes above to extract information")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🔍 Resume Filter | Powered by AI Agent + Groq Llama</p>
</div>
""", unsafe_allow_html=True)
