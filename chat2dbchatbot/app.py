import streamlit as st
from typing import Dict
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from tools.db import DatabaseManager
from tools.rag import RAGSearch

# Load environment variables
load_dotenv()

import openai

@dataclass
class ChatConfig:
    """Configuration for chat application"""
    interaction_method: str
    llm_provider: str
    #model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.0

def main():
    # Database setup
    db_manager = DatabaseManager(db_type='vecdb')
    if not db_manager.test_connection():
        st.error("Database connection failed")
        return
    
    # OpenAI setup
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        st.error("OPENAI_API_KEY not found in environment variables")
        return
    
    # Initialize RAGSearch
    rag_search = RAGSearch(db_manager)
    
    # Streamlit UI
    st.title("🤖 Chat To Your Database 🤖")

    with st.sidebar:    
        interaction_method = st.selectbox(
            "Interaction Method",
            ["RAG","TAG","Fine-tuning"],
            key="interaction_method"
        )
        
        llm_provider = st.selectbox(
            "LLM Provider",
            ["OpenAI", "Claude"],
            disabled=interaction_method == "Fine-tuning",
            key="llm_provider"
        )
        
        with st.expander("Advanced Settings"):
            temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    
    # Chat interface
    if query := st.chat_input("Ask a question about your database"):
        config = ChatConfig(
            interaction_method=interaction_method,
            llm_provider=llm_provider,
            temperature=temperature
        )
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        
        with st.spinner("Processing your question..."):
            # Query the vector index
            response = rag_search.query(query)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display chat history
        for message in st.session_state.messages:
            st.write(f"{message['role']}: {message['content']}")

if __name__ == "__main__":
    if "messages" not in st.session_state:
        st.session_state.messages = []
    main()