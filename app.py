import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to query the PaLM API using the provided API key and model
def query_palm_api(context, question):
    # Set the API key for Google PaLM
    genai.configure(api_key="AIzaSyDFyy38UAFQZiybGucZUUVOaouwFV5KCRE")
    try:
        # Create the model object for 'gemini-1.5-flash'
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Generate a response using the model
        response = model.generate_content(f"Context: {context}\n\nQuestion: {question}")
        return response.text if response else "No response generated."
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="Document Q&A", layout="wide")
st.title("📄 Chat With Pdf's")
st.write("**Upload a PDF or Text file, and ask questions about its content.**")

# File upload section with improved layout
uploaded_file = st.file_uploader(
    "Upload a PDF or Text file", 
    type=["pdf", "txt"], 
    label_visibility='collapsed',
    help="Supports PDF and text files up to 10MB."
)

# Handle file upload and extract content
if uploaded_file:
    with st.expander("📚 File Content", expanded=False):
        if uploaded_file.type == "application/pdf":
            extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            extracted_text = uploaded_file.read().decode('utf-8')

        st.text_area("Extracted Content", extracted_text[:1000] + "...", height=200, disabled=True)

    # Store conversation in session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display conversation history with improved formatting
    st.subheader("🗣️ Conversation History")
    for i, (user_q, ai_response) in enumerate(st.session_state.conversation):
        st.write(f"**Q{i+1}:** {user_q}")
        st.write(f"**A{i+1}:** {ai_response}")
        st.markdown("---")

    # Input for a new question with a larger text input
    st.subheader("💬 Ask a Question")
    new_question = st.text_area(
        "Type your question here and click 'Get Answer'", 
        key=f"question_{len(st.session_state.conversation)}", 
        height=100
    )
    
    if st.button("Get Answer", key=f"button_{len(st.session_state.conversation)}") and new_question.strip():
        with st.spinner("🤖 Generating the answer..."):
            answer = query_palm_api(extracted_text, new_question)
            st.session_state.conversation.append((new_question, answer))
        
        # Display the latest Q&A immediately without rerun
        st.write(f"**Q{len(st.session_state.conversation)}:** {new_question}")
        st.write(f"**A{len(st.session_state.conversation)}:** {answer}")
        st.markdown("---")
else:
    st.info("Please upload a file to start asking questions.")
