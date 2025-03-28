import streamlit as st
import json
from io import BytesIO
from docx import Document
from fpdf import FPDF
from openai import OpenAI, OpenAIError

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

fields = [
    "customer_name", "industry", "company_background", "key_business_services",
    "current_challenges", "decision_criteria", "tech_stack",
    "desired_outcomes", "scope_of_architecture", "timeline", "key_contacts"
]

for field in fields:
    if field not in st.session_state:
        st.session_state[field] = ""

st.title("POC Scoping Document Generator")

uploaded_file = st.file_uploader("Upload call transcript or notes (TXT only)", type=["txt"])
raw_input_text = st.text_area("Or paste notes/transcript manually")
auto_extract = st.button("Extract Info and Populate Fields")

if auto_extract:
    if uploaded_file:
        input_text = uploaded_file.read().decode("utf-8")
    elif raw_input_text:
        input_text = raw_input_text
    else:
        st.warning("Please upload or paste some content.")
        st.stop()

    prompt = f"""
    You're an assistant extracting information from notes for a POC document.

    Input:
    {input_text}

    Output the following as a JSON object:
    {{
        "customer_name": "...",
        "industry": "...",
        "company_background": "...",
        "key_business_services": "...",
        "current_challenges": "...",
        "decision_criteria": "...",
        "tech_stack": "...",
        "desired_outcomes": "...",
        "scope_of_architecture": "...",
        "timeline": "...",
        "key_contacts": "..."
    }}
    """

    try:
        response = client.chat.completions.create(
          model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response.choices[0].message.content
        extracted_json = json.loads(content)
        for key in extracted_json:
            st.session_state[key] = extracted_json[key]
        st.success("Fields auto-filled! Scroll down to review and edit.")
    except OpenAIError as e:
        st.error(f"OpenAI API Error: {str(e)}")
    except json.JSONDecodeError:
        st.error("Failed to parse GPT response as JSON.")
        st.text(content)
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

# Form fields
st.header("Review & Edit Extracted Info")

customer_name = st.text_input("Customer Name", value=st.session_state["customer_name"])
industry = st.text_input("Industry", value=st.session_state["industry"])
company_background = st.text_area("Company Background", value=st.session_state["company_background"])
key_business_services = st.text_area("Key Business Services", value=st.session_state["key_business_services"])
current_challenges = st.text_area("Current Challenges", value=st.session_state["current_challenges"])
decision_criteria = st.text_area("Decision Criteria", value=st.session_state["decision_criteria"])
tech_stack = st.text_area("Tech Stack", value=st.session_state["tech_stack"])
desired_outcomes = st.text_area("Desired Outcomes", value=st.session_state["desired_outcomes"])
scope_of_architecture = st.text_area("Scope of Architecture", value=st.session_state["scope_of_architecture"])
timeline = st.text_area("Timeline", value=st.session_state["timeline"])
key_contacts = st.text_area("Key Contacts", value=st.session_state["key_contacts"])

if st.button("Generate POC Document"):
    document = f"""
1. Executive Summary

{desired_outcomes}

2. Company Background

{company_background}

3. Key Business Services

{key_business_services}

4. Current Situation / Challenges

{current_challenges}

5. Decision Criteria

{decision_criteria}

6. Scope of Architecture

{scope_of_architecture}

7. Timeline

{timeline}

8. POV Team

{key_contacts}
    """
    st.subheader("Generated Document")
    st.markdown(document)

    # DOCX download
    docx_file = Document()
    for section in document.strip().split("\n\n"):
        docx_file.add_paragraph(section)
    docx_buffer = BytesIO()
    docx_file.save(docx_buffer)
    docx_buffer.seek(0)

    st.download_button("📄 Download as Word Document", docx_buffer, file_name="POC_Scoping_Document.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    # PDF download
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in document.strip().split("\n"):
        pdf.multi_cell(0, 10, line)
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    st.download_button("📄 Download as PDF", pdf_buffer, file_name="POC_Scoping_Document.pdf", mime="application/pdf")

    st.info("🚀 Want to enable saving to Google Drive? You'll need to set up Google OAuth and use PyDrive2. Happy to help you with that next!")
