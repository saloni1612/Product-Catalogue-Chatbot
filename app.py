import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import asyncio
import threading

if threading.current_thread() is not threading.main_thread():
    asyncio.set_event_loop(asyncio.new_event_loop())

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Setup LLM and embedding model
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)



# UI setup
st.set_page_config(page_title="📦 Product Catalogue Chatbot", layout="wide")
st.title("🛍️ Product Catalogue Chatbot")

mode = st.sidebar.radio("Select Mode", ["Business (Upload Catalog)", "Customer (Ask Questions)"])

# ---------------------- BUSINESS MODE ----------------------
if mode == "Business (Upload Catalog)":
    st.header("📤 Upload Product Catalogue")
    business_name = st.text_input("Business Name (unique ID)", max_chars=50)

    uploaded_file = st.file_uploader("Upload PDF Catalog", type=["pdf"])
    process_btn = st.button("📥 Process & Embed Catalog")

    if process_btn and uploaded_file and business_name:
        with st.spinner("Reading and processing PDF..."):
            # Read PDF
            pdf_reader = PdfReader(uploaded_file)
            raw_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    raw_text += text

            # Split into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = splitter.split_text(raw_text)

            # Create vector store
            vectordb = FAISS.from_texts(texts, embedding=embedding_model)

            # Save to local folder
            save_path = f"business_data/{business_name}"
            os.makedirs("business_data", exist_ok=True)
            vectordb.save_local(save_path)

            st.success(f"✅ Uploaded and embedded catalogue for business: {business_name}")

# ---------------------- CUSTOMER MODE ----------------------
else:
    st.header("💬 Ask a Question About a Product Catalogue")

    selected_business = st.text_input("Enter Business Name")
    user_question = st.text_input("Ask your question")

    ask_btn = st.button("🧠 Get Answer")

    if ask_btn and selected_business and user_question:
        try:
            # Load vectorstore
            vectordb = FAISS.load_local(f"business_data/{selected_business}", embeddings=embedding_model, allow_dangerous_deserialization=True)

            # Search similar chunks
            docs = vectordb.similarity_search(user_question, k=3)

            # QA Prompt
            prompt_template = """
You are a helpful assistant for a product catalogue. Use the context below to answer the customer's question.
Context: {context}
Question: {question}
Answer:"""
            prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

            # QA Chain
            qa_chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt)

            # Run chain
            response = qa_chain.run(input_documents=docs, question=user_question)

            st.success("🗨️ Answer:")
            st.write(response)

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
