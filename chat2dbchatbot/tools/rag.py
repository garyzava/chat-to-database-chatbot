# tools/rag.py
import os
from dotenv import load_dotenv
from tools.ingest import VectorSearch
from tools.db import DatabaseManager

# Load environment variables
load_dotenv()

import openai

class RAGSearch(VectorSearch):
    def query(self, query_text: str) -> str:
        """Query the vector index with better handling."""
        index = self.load_index()
        query_engine = index.as_query_engine()
        response = query_engine.query(query_text)
        return response

def main():
    # Database setup
    db_manager = DatabaseManager(db_type='vecdb')
    if not db_manager.test_connection():
        raise ConnectionError("Database connection failed")
        
    # OpenAI setup
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Initialize RAGSearch
    rag_search = RAGSearch(db_manager)
    
    # Example query
    result = rag_search.query("What is the album table?")
    print(result)

if __name__ == "__main__":
    main()