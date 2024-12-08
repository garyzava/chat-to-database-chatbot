import os
import re
from tools.ingestsql import VectorSearch
from tools.db import DatabaseManager

from sqlalchemy import create_engine

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine

from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

from dotenv import load_dotenv
load_dotenv()

def is_null_or_empty(s):
    return s is None or s.strip() == ""

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
    
def extract_sql_query(response_text: str) -> str:
    """
    Find the first continuous block of SQL-like text
    """
    sql_lines = []
    in_sql_block = False
    for line in response_text.split('\n'):
        line = line.strip()
        if line.upper().startswith('SELECT ') or line.upper().startswith('WITH '):
            in_sql_block = True
        
        if in_sql_block:
            sql_lines.append(line)
            if line.endswith(';'):
                break
        
        # Join and clean the SQL query
        sql_query = ' '.join(sql_lines)
        sql_query = re.sub(r'\s+', ' ', sql_query).strip()

def extract_sql_query_o(response_text: str) -> str:
        """
        Look for SQL query between code blocks (```sql or ```)
        """
        # Strategy 1: Extract from code blocks
        code_block_patterns = [
            r'```sql(.*?)```',  # Markdown code block with sql
            r'```(.*?)```',     # Generic code block
            r'`(SELECT.*?);`',  # Inline code with SQL
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
def extract_sql_query_t(response_text: str) -> str:
        """
        Use regex to find SQL-like statements
        """
        sql_pattern = r'(SELECT\s+.*?;)'
        match = re.search(sql_pattern, response_text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        else:
            return ""
    

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

    sql_query_str = str(sql_query)

    if(llm_provider == "OpenAI"):
        return sql_query_str
    else:
        extracted = extract_sql_query_t(sql_query_str)
        if is_null_or_empty(extracted):
            return "no sql"
        else: 
            return extracted