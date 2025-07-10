import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

# Load environment variables
load_dotenv()
API_VERSION = os.getenv("api_version")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("endpoint")

def get_pdf_text(pdf_docs):
    """Extract text from uploaded PDF files."""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

def get_text_chunks(text):
    """Split text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    """Convert text chunks into embeddings and store them in FAISS."""
    embeddings = AzureOpenAIEmbeddings(
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
    )
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    """Create a conversational chain with Azure ChatGPT."""
    prompt_template = PromptTemplate(
        template="""
        Answer the question as detailed as possible from the provided context. If the answer is not in
        the context, just say, "Answer is not available in the context."

        Question:
        {question}

        Answer:
        """,
        input_variables=["question"],
    )
    llm = AzureChatOpenAI(
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        temperature=0.4,
        model="gpt-4o",
    )
    return llm, prompt_template

def user_input(user_question):
    """Process user input and return AI-generated response."""
    try:
        embeddings = AzureOpenAIEmbeddings(
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT,
            api_key=AZURE_API_KEY,
        )
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)

        llm, prompt_template = get_conversational_chain()
        response = llm.predict(prompt_template.format(question=user_question))
        
    except Exception as e:
        response = f"Error processing the request: {str(e)}"
    
    st.write("Reply:", response)

def main():
    """Main Streamlit app function."""
    st.set_page_config(page_title="Chat PDF")
    st.header("Chat with PDF using Azure AI 💁")

    user_question = st.text_input("Ask a Question from the PDF Files")
    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Processing Complete! You can now ask questions.")

if __name__ == "__main__":
    main()
