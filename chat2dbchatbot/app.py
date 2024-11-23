import streamlit as st
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from tools.db import DatabaseManager
from tools.rag import RAGSearch # RAG
from tools.tag import create_tag_pipeline # TAG

# Load environment variables
load_dotenv()

#import openai
import asyncio


@dataclass
class ChatConfig:
    """Configuration for chat application"""
    interaction_method: str
    llm_provider: str
    # openai_model_name: str = "gpt-3.5-turbo"
    openai_model_name: str = "gpt-4"
    #claude_model_name: str = "claude-3-opus-20240229"
    claude_model_name: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.1

class ChatDatabase:
    def __init__(self):

        # Initialize Vector Database
        print("KM: Initialize Vector DB")
        try:
            self.vec_db_manager = DatabaseManager(db_type='vecdb')
            self.vec_db_manager.test_connection()
        except Exception as e:
            st.error(f"Error connecting to vector store: {str(e)}")
            self.vec_db_manager = None
        
        # Initialize Chat Database
        print("KM: Initialize Chat Database")
        try:
            self.chat_db_manager = DatabaseManager(db_type='db')
            self.chat_db_manager.test_connection()
        except Exception as e:
            st.error(f"Error connecting to SQL database: {str(e)}")
            self.chat_db_manager = None

    def rag_pipeline(self, query: str, config: ChatConfig) -> str:
        """RAG pipeline for database queries"""
        try:
            print("KM: Starting in rag_pipeline function")
            #rag_search = RAGSearch(self.vec_db_manager, self.chat_db_manager)
            rag_search = RAGSearch(self.vec_db_manager, self.chat_db_manager, config=config)

            response = rag_search.query(f"You are Postgres expert. Generate a SQL based on the following question using the additional metadata given to you: {query}")
            st.write("Generated response:-", response)
            print("Generated response:- ", response)
            sql_query = str(response).strip("`sql\n").strip("`") #not needed
            print("Generated SQL:- ", sql_query)
            # Execute SQL query
            sql_result = rag_search.sql_query(str(sql_query))
            print("SQL Result:- ", sql_result)

            return sql_result
        #except Exception as e:
        #    st.error(f"Error in RAG pipeline: {str(e)}")
        #    return None
        except Exception as e:
            return f"Error in RAG pipeline: {str(e)}"        


    async def tag_pipeline(self, query: str, config: ChatConfig) -> str:
        """TAG pipeline for database queries"""
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
            
            # Execute workflow
            handler = tag_workflow.run(query=query)
            
            # Stream events if workflow is verbose
    #        if tag_workflow._verbose:
    #            async for event in handler.stream_events():
    #                if isinstance(event, QuerySynthesisEvent):
    #                    st.write("Generated SQL:", event.sql_query)
    #                elif isinstance(event, QueryExecutionEvent):
    #                    st.write("Query Results:", event.results)
                        
            # Get final response
            response = await handler
            return str(response)

            # Get final response with timeout
#            try:
#                response = await asyncio.wait_for(handler, timeout=120.0)
#                return str(response)
#            except asyncio.TimeoutError:
#                return "The operation timed out. Please try again or simplify your query."

        except Exception as e:
            return f"Error in TAG pipeline: {str(e)}"

def main():
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
            #llm = chat.get_llm(config)
            #if not chat.intent_classifier(query, llm):
            if not True:
                response = "This question doesn't appear to be database-related. Please try a database-related question."
            else:
                # Process based on method
                if interaction_method == "RAG":
                    print("KM: about to call RAG")
                    response = chat.rag_pipeline(query, config)
                elif interaction_method == "TAG":
                    #response = await chat.tag_pipeline(query, config)

                    response = asyncio.run(chat.tag_pipeline(query, config))
                else:
                    response = "Fine-tuning pipeline not yet implemented"
        # Display chat history
        #for message in st.session_state.messages:
            #st.write(f"{message['role']}: {message['content']}")
            #st.session_state.messages.append({"role": "assistant", "content": response})
        #    message.append({"role": "assistant", "content": response})

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display chat history
        for message in st.session_state.messages:
            st.write(f"{message['role']}: {message['content']}")



if __name__ == "__main__":
    if "messages" not in st.session_state:
        st.session_state.messages = []
    main()