import streamlit as st
from dataclasses import dataclass

from dotenv import load_dotenv
from tools.db import DatabaseManager
from tools.rag import RAGSearch # RAG
from tools.tag import create_tag_pipeline # TAG

# Load environment variables
load_dotenv()

import asyncio

import pickle
from pathlib import Path

from langfuse.llama_index import LlamaIndexInstrumentor
from langfuse.decorators import langfuse_context, observe

@dataclass
class ChatConfig:
    """Configuration for chat application"""
    interaction_method: str
    llm_provider: str
    openai_model_name: str = "gpt-4"
    claude_model_name: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.1

class ChatDatabase:
    def __init__(self):

        # Initialize Vector Database
        try:
            self.vec_db_manager = DatabaseManager(db_type='vecdb')
            self.vec_db_manager.test_connection()
        except Exception as e:
            st.error(f"Error connecting to vector store: {str(e)}")
            self.vec_db_manager = None
        
        # Initialize Chat Database
        try:
            self.chat_db_manager = DatabaseManager(db_type='db')
            self.chat_db_manager.test_connection()
        except Exception as e:
            st.error(f"Error connecting to SQL database: {str(e)}")
            self.chat_db_manager = None

        # Load classifier model
        self.classifier = self.load_classifier()
        
        # Initialize Langfuse instrumentor
        self.instrumentor = LlamaIndexInstrumentor()
        self.instrumentor.start()
        print("Langfuse instrumentor checkpoint: Disregard Langfuse error messages on dev mode.")        


    def load_classifier(self):
        """Load the classifier model from a pickle file."""
        current_dir = Path(__file__).parent
        model_path = current_dir / 'classifier/combined_sql_classifier.pkl'
        with open(model_path, 'rb') as file:
            objects = pickle.load(file)
        return objects

    def classify_prompt(self, prompt):
        """Classify the prompt using the loaded classifier."""
        vectorizer = self.classifier["vectorizer"]
        binary_classifier = self.classifier["binary_classifier"]
        classifier_domain = self.classifier["classifier_domain"]
        classifier_complexity = self.classifier["classifier_complexity"]
        classifier_task_type = self.classifier["classifier_task_type"]
        label_encoder_domain = self.classifier["label_encoder_domain"]
        label_encoder_complexity = self.classifier["label_encoder_complexity"]
        label_encoder_task_type = self.classifier["label_encoder_task_type"]

        # Transform the prompt using the vectorizer
        prompt_tfidf = vectorizer.transform([prompt])

        # Binary Classification (SQL vs Non-SQL)
        is_sql = binary_classifier.predict(prompt_tfidf)[0]

        # If not SQL, return early
        if is_sql == 0:
            print("Classification Results: Non-SQL Query")
            return False

        # Predict using the classifiers
        domain_prediction = classifier_domain.predict(prompt_tfidf)[0]
        complexity_prediction = classifier_complexity.predict(prompt_tfidf)[0]
        task_type_prediction = classifier_task_type.predict(prompt_tfidf)[0]

        # Decode predictions
        domain = label_encoder_domain.inverse_transform([domain_prediction])[0]
        complexity = label_encoder_complexity.inverse_transform([complexity_prediction])[0]
        task_type = label_encoder_task_type.inverse_transform([task_type_prediction])[0]

        print("Classification Results: SQL Query")
        print(f"Domain: {domain}")
        print(f"Complexity: {complexity}")
        print(f"Task Type: {task_type}")

        return True


    def rag_pipeline(self, query: str, config: ChatConfig) -> str:
        """RAG pipeline for database queries
            The following function is adapted from LlamaIndex's example repository:
            https://docs.llamaindex.ai/en/stable/examples/        
        """
        try:
            rag_search = RAGSearch(self.vec_db_manager, self.chat_db_manager, config=config)

            response = rag_search.query(f"You are Postgres expert. Generate a SQL based on the following question using the additional metadata given to you: {query}")
            print("App.py Generated response:- ", response)
            sql_query = str(response).strip("`sql\n").strip("`") #optional
            print("App.py Generated SQL:- ", sql_query)
            # Execute SQL query
            sql_result = rag_search.sql_query(str(sql_query))
            print("App.py SQL Result:- ", sql_result)

            return sql_result
        
        except Exception as e:
            return f"Error in RAG pipeline: {str(e)}"        

    @observe()
    async def tag_pipeline(self, query: str, config: ChatConfig) -> str:
        """TAG pipeline for database queries
            The following function is adapted from LlamaIndex's workflow documenetation:
            https://docs.llamaindex.ai/en/stable/examples/workflow/advanced_text_to_sql/
            Additionally, this function uses Langfuse's documentation for integration with Llamaindex:
            https://langfuse.com/docs/integrations/llama-index/get-started/        
        """
        try:
            # Verify database connections
            if not self.vec_db_manager or not self.chat_db_manager:
                return "Error: Database connections not initialized"
                
            # Initialize TAG workflow
            tag_workflow = create_tag_pipeline(
                vec_db_manager=self.vec_db_manager,
                chat_db_manager=self.chat_db_manager,
                config=config
            )

            current_trace_id = langfuse_context.get_current_trace_id()
            current_observation_id = langfuse_context.get_current_observation_id()
            with self.instrumentor.observe(
                trace_id=current_trace_id,
                parent_observation_id=current_observation_id,
                update_parent=False,
            ):
                # Execute workflow
                handler = tag_workflow.run(query=query)
                # Get final response
                response = await handler
                return str(response)
            
        except Exception as e:
            return f"Error in TAG pipeline: {str(e)}"

def main():
    # Session state for the chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Session state initialization for the Intent Classifier toggle
    if "intent_classifier_enabled" not in st.session_state:
        st.session_state.intent_classifier_enabled = False

    # Streamlit UI
    st.title("🤖 Chat To Your Database 🤖")

    with st.sidebar:    
        interaction_method = st.selectbox(
            "Interaction Method",
            ["RAG","TAG"],
            key="interaction_method"
        )
        
        llm_provider = st.selectbox(
            "LLM Provider",
            ["OpenAI", "Claude"],
            key="llm_provider"
        )
        
        with st.expander("Advanced Settings"):
            temperature = st.slider(
                "Temperature", 
                min_value=0.0,
                max_value=1.0,
                value=0.1,  # Default value
                step=0.1
            )
            #intent classifier toggle
            st.session_state.intent_classifier_enabled = st.toggle(
                "Intent Classifier",
                value=st.session_state.intent_classifier_enabled,
                help="Enable/disable intent classification"
            )         

    # Initialize chat interface
    chat = ChatDatabase()

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
            # Check intent first
            should_process_llm = True
            if st.session_state.intent_classifier_enabled:
                # Only check classification if the classifier is enabled
                should_process_llm = chat.classify_prompt(query)
                if not should_process_llm:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "Message from Classifier: This question doesn't appear to be database-related."
                    })
            
            if should_process_llm:
            # Process query based on selected method
                response = (
                    chat.rag_pipeline(query, config) if interaction_method == "RAG"
                    else asyncio.run(chat.tag_pipeline(query, config))
                )
                # Add assistant response to chat history             
                if isinstance(response, str): # If it's an error message or custom string
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else: # If it's a regular Response object
                    st.session_state.messages.append({"role": "assistant", "content": response.response})

    # Display the entire chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

if __name__ == "__main__":
    # Session state initialization for the Intent Classifier toggle
    if "intent_classifier_enabled" not in st.session_state:
        st.session_state.intent_classifier_enabled = False
    main()