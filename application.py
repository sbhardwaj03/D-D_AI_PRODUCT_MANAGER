import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from groq import Groq
import numpy as np
import chromadb  # Vector database

# Secure API Key Storage
API_KEY = 'gsk_bURZU3TF0hHDaZvtXQ8WGdyb3FYbaGzNbL2pXQl9k4ONJ5I3B0T'
if not API_KEY:
    st.error("API key not found. Please set the 'GROQ_API_KEY' environment variable.")
    st.stop()

# Initialize Groq Client
client = Groq(api_key=API_KEY)

# Initialize Vector Database (ChromaDB)
chroma_client = chromadb.PersistentClient(path="./chroma_db")  # Persistent storage
collection = chroma_client.get_or_create_collection(name="knowledge_base")

# Example External Knowledge Base
knowledge_base = {
    "short_project": "For short projects, prioritize core features and allocate tasks efficiently.",
    "agile_methodology": "Use agile methodologies for iterative development and quick feedback loops.",
    "teamwork": "Encourage open communication and collaboration among team members.",
}

# Function to Get Embeddings from Groq
def get_embedding(text):
    """Generates text embeddings using Groq API."""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": f"Generate a numerical embedding for: {text}"}]
    )
    return np.array([float(x) for x in response.choices[0].message.content.split()])  # Convert to list

# Store Knowledge Base in Vector Database (if not already stored)
def store_knowledge():
    if collection.count() == 0:  # Avoid duplicate storage
        for key, value in knowledge_base.items():
            vector = get_embedding(value).tolist()
            collection.add(ids=[key], embeddings=[vector], metadatas=[{"content": value}])

store_knowledge()  # Ensure database is populated

# Function to Retrieve Relevant Data Using Vector Search
def retrieve_relevant_data(query):
    query_vector = get_embedding(query).tolist()
    
    # Search for top 2 most relevant documents
    results = collection.query(query_embeddings=[query_vector], n_results=2)
    
    # Extract and return relevant content
    relevant_data = "\n".join([doc['content'] for doc in results['metadatas'][0]])
    return relevant_data if relevant_data else "No relevant data found."

# Question Answering System
def question_answering_system(query):
    try:
        # Retrieve relevant data from vector database
        relevant_data = retrieve_relevant_data(query)
        
        # Augment query with context
        augmented_query = f"""
        {query}

        Given the context:
        {relevant_data}

        Create a structured product roadmap for '{st.session_state.product_name}'.
        **Format the roadmap in "Phase X" style** (e.g., Phase 1, Phase 2).
        Each phase should include:
        - **Phase Name**
        - **Timeline** (YYYY-MM-DD to YYYY-MM-DD)
        - **Tasks**
        - **Deliverables**

        Project starts on {st.session_state.start_date} and ends on {st.session_state.end_date}.
        Team: {st.session_state.team}.
        """
        
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[{'role': 'user', 'content': augmented_query}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit Page Configuration
st.set_page_config(page_title="AI Product Manager", page_icon="🤖", layout="wide")

# Initialize session state variables
if 'product_name' not in st.session_state:
    st.session_state.product_name = ""
if 'start_date' not in st.session_state:
    st.session_state.start_date = None
if 'end_date' not in st.session_state:
    st.session_state.end_date = None
if 'team' not in st.session_state:
    st.session_state.team = ""
if 'roadmap_generated' not in st.session_state:
    st.session_state.roadmap_generated = False

# Input Page
def input_page():
    st.title("🤖 AI Product Manager")
    st.write("Enter details to generate a **structured product roadmap**.")

    with st.form("product_details"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.product_name = st.text_input("Product Name:", value=st.session_state.product_name)
            st.session_state.start_date = st.date_input("📅 Start Date:", value=st.session_state.start_date)
            st.session_state.end_date = st.date_input("📅 End Date:", value=st.session_state.end_date)
        with col2:
            product_description = st.text_area("📝 Product Description:")

        if st.session_state.start_date and st.session_state.end_date:
            if st.session_state.end_date < st.session_state.start_date:
                st.error("🚨 End date cannot be earlier than start date.")

        st.subheader("👥 Build Your Team")
        roles = ["Backend Developer", "Frontend Developer", "Tester", "UI/UX Designer", "Data Analyst", "DevOps Engineer"]
        selected_roles = [role for role in roles if st.checkbox(role)]

        submit_button = st.form_submit_button("🚀 Generate Roadmap")

    if submit_button:
        if st.session_state.product_name and product_description and st.session_state.start_date and st.session_state.end_date:
            st.session_state.team = ", ".join(selected_roles) if selected_roles else "No team selected"
            st.session_state.roadmap_generated = True
            st.rerun()

# Roadmap Page
def roadmap_page():
    st.title("📌 Generated Roadmap")
    query = f"Create a roadmap for '{st.session_state.product_name}'. Starts: {st.session_state.start_date}, Ends: {st.session_state.end_date}, Team: {st.session_state.team}."

    answer = question_answering_system(query)
    st.write(answer)

# Main App Logic
if not st.session_state.roadmap_generated:
    input_page()
else:
    roadmap_page()
