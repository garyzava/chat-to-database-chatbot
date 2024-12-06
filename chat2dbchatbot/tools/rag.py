import os
from tools.ingest import VectorSearch
from tools.db import DatabaseManager

from sqlalchemy import create_engine

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine

from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

from dotenv import load_dotenv
load_dotenv()

class RAGSearch(VectorSearch):
    def __init__(self, vec_db_manager, chat_db_manager, config, *args, **kwargs):
        super().__init__(vec_db_manager, *args, **kwargs)
        self.chat_db_manager = chat_db_manager
        self.config = config

        # Assign LLM model
        if self.config.llm_provider == "OpenAI":
            self.llm = OpenAI(temperature=self.config.temperature, model=self.config.openai_model_name)
        elif self.config.llm_provider == "Claude":
            self.llm = Anthropic(temperature=self.config.temperature, model=self.config.claude_model_name)

    def query(self, query_text: str) -> str:
        """Query the vector index"""

        index = self.load_index()
        query_engine = index.as_query_engine(llm=self.llm)
        response = query_engine.query(query_text)

        return response

    def sql_query(self, query_text: str) -> str:
        """Perform a text-to-SQL query on the connected database."""

        conn =  create_engine(self.chat_db_manager.get_connection_string())

        sql_database = SQLDatabase(conn)
        table_names = self.chat_db_manager.get_table_names()
        query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database, 
            tables=table_names,
            sql_only=False,
            llm=self.llm
        )
        response = query_engine.query(query_text)
        return response

def run_rag_pipeline(query: str, llm_provider: str = "OpenAI", temperature: float = 0.1) -> str:
    """Run the RAG pipeline with given parameters."""
    # Create config
    config = type('Config', (), {
        'llm_provider': llm_provider,
        'temperature': temperature,
        'openai_model_name': 'gpt-4',
        'claude_model_name': 'claude-3-sonnet-20240229'
    })()

    # Initialize databases
    vec_db_manager = DatabaseManager(db_type='vecdb')
    chat_db_manager = DatabaseManager(db_type='db')
    
    if not vec_db_manager.test_connection():
        raise ConnectionError("Vector Database connection failed")
    if not chat_db_manager.test_connection():
        raise ConnectionError("Database connection failed")
    
    # Initialize RAGSearch
    rag_search = RAGSearch(vec_db_manager, chat_db_manager, config)
    
    # Generate and execute query
    sql_query = rag_search.query(
        f"You are Postgres expert. Generate a SQL based on the following question using the additional metadata given to you: {query}"
    )
    print(f"Generated SQL: {sql_query}")
    
    sql_result = rag_search.sql_query(str(sql_query))
    print(f"Final Result: {sql_result}")

def rag_parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='RAG Pipeline CLI')
    parser.add_argument('query', help='Natural language query for the database')
    parser.add_argument('--llm', default='OpenAI', choices=['OpenAI', 'Claude'],
                      help='LLM provider to use (default: OpenAI)')
    parser.add_argument('--temperature', type=float, default=0.1,
                      help='Temperature for LLM (default: 0.1)')

    return parser.parse_args()

def main():
    os.environ['ENV'] = 'dev'
    args = rag_parse_args()
    try:
        run_rag_pipeline(args.query, args.llm, args.temperature)
    except Exception as e:
        print(f"Error in RAG main(): {e}")
        return 1
    return 0

if __name__ == "__main__":
    import sys
    import argparse
    sys.exit(main())