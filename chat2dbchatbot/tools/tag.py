import os

from sqlalchemy import create_engine

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine

from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

from llama_index.core.workflow import (
    Workflow, 
    StartEvent,
    StopEvent,
    step,
    Context,
    Event
)

from typing import List, Union

from dotenv import load_dotenv
load_dotenv()

class QuerySynthesisEvent(Event):
    """Event containing synthesized SQL query"""
    sql_query: str
    query: str
    relevant_tables: List[str]

class QueryExecutionEvent(Event):
    """Event containing query execution results"""
    results: List[tuple]  # Explicitly typed as List to satisfy validation
    query: str 
    sql_query: str

class TAGWorkflow(Workflow):
    """Table-Augmented Generation (TAG) workflow implementation"""
    
    def __init__(
        self,
        vec_db_manager,
        chat_db_manager, 
        llm,  
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.vec_db_manager = vec_db_manager
        self.chat_db_manager = chat_db_manager
        self.llm = llm
        
        # Create engine using the connection string from chat_db_manager
        conn =  create_engine(self.chat_db_manager.get_connection_string())
        sql_database = SQLDatabase(conn)
        
        # Initialize query engine with table names from chat_db_manager
        self.query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database,
            tables=self.chat_db_manager.get_table_names(),
            llm=self.llm
            ,sql_only=True # Set to True to only generate SQL queries
        )
    
    def _is_valid_sql(self, sql: str) -> bool:
        """
        Check if string is a valid read-only SQL query.
        Handles SELECT statements, CTEs (WITH), and CTAS patterns.
        """
        if not sql:
            return False
        
        sql = sql.strip().upper()
        return (
            sql.startswith('SELECT') or 
            sql.startswith('WITH') or
            sql.startswith('CREATE TABLE') and 'AS SELECT' in sql
        )

    @step
    # Union types added for handling error cases
    async def query_synthesis(self, ctx: Context, ev: StartEvent) -> Union[QuerySynthesisEvent, StopEvent]:
        """Step 1: Query Synthesis - Translate natural language to SQL"""
        try:
            # Store original query in context
            await ctx.set("original_query", ev.query)
            
            # Get all available tables
            all_tables = self.chat_db_manager.get_table_names()
            
            # Generate SQL using LLM
            response = await self.query_engine.aquery(ev.query)
            print("response:-", response)

            # Get the sql part from the response
            sql_query = response.metadata.get("sql_query", "")
            print("Generated SQL:-", sql_query)

            # Analyze SQL from response
            valid_sql = self._is_valid_sql(sql_query)
            print("valid_sql:-", valid_sql)
            if not valid_sql:
                # If no valid SQL was generated, return early with error message
                return StopEvent(
                    result="I cannot generate a valid SQL query for this question. The required information might not be available in the database."
                )
            
            # Extract relevant tables from the SQL query
            relevant_tables = [
                table for table in all_tables 
                if table.lower() in sql_query.lower()
            ]
            
            # Store in context for potential future use
            await ctx.set("sql_query", sql_query)
            await ctx.set("relevant_tables", relevant_tables)
            
            return QuerySynthesisEvent(
                sql_query=sql_query,
                query=ev.query,
                relevant_tables=relevant_tables
            )
        except Exception as e:
            print(f"Error in query synthesis: {str(e)}")
            return StopEvent(
                result=f"Error generating SQL query: {str(e)}"
            )

    @step 
    async def query_execution(self, ctx: Context, ev: QuerySynthesisEvent) -> Union[QueryExecutionEvent, StopEvent]:
        """Step 2: Query Execution - Execute SQL query against database"""
        try:
            # Execute query using db manager
            results = self.chat_db_manager.execute_query(ev.sql_query)
            
            # Handle case where no results were returned
            if results is None:
                results = []
                
            # Validate results is a list
            if not isinstance(results, list):
                results = list(results) if results else []
                
            return QueryExecutionEvent(
                results=results,
                query=ev.query,
                sql_query=ev.sql_query
            )
            
        except Exception as e:
            print(f"Error in query execution: {str(e)}")
            return StopEvent(
                result=f"Error executing SQL query: {str(e)}"
            )

    @step
    async def answer_generation(self, ctx: Context, ev: QueryExecutionEvent) -> StopEvent:
        """Step 3: Answer Generation - Generate natural language response"""
        try:
            # Get original query from context
            original_query = await ctx.get("original_query")
            
            # Format query results
            result_str = "\n".join([str(r) for r in ev.results]) if ev.results else "No results found"
            
            # Generate response using LLM
            prompt = f"""
            Generate a clear and natural language response to this question.
            If no results were found, explain what information is missing from the database.
            
            Original Question: {original_query}
            SQL Query Used: {ev.sql_query}
            Query Results: {result_str}
            """

            response = await self.llm.acomplete(prompt)

            return StopEvent(result=str(response))
            
        except Exception as e:
            print(f"Error in answer generation: {str(e)}")
            return StopEvent(
                result=f"Error generating response: {str(e)}"
            )

def create_tag_pipeline(vec_db_manager, chat_db_manager, config):
    """Factory function to create TAG workflow instance"""
    # Initialize workflow with selected LLM
    if config.llm_provider == "OpenAI":

        llm = OpenAI(
            model=config.openai_model_name,
            temperature=config.temperature
        )
    else:
        llm = Anthropic(
            model=config.claude_model_name,
            temperature=config.temperature
        )

    workflow = TAGWorkflow(
        vec_db_manager=vec_db_manager,
        chat_db_manager=chat_db_manager,
        llm=llm,
        verbose=True
        ,timeout=None # No timeout for now
    )

    return workflow

async def run_tag_pipeline(query: str, llm_provider: str = "OpenAI", temperature: float = 0.1) -> str:
    """Run the TAG pipeline with given parameters"""
    # Database setup 
    from tools.db import DatabaseManager
    vec_db_manager = DatabaseManager(db_type='vecdb')
    chat_db_manager = DatabaseManager(db_type='db')

    if not vec_db_manager.test_connection():
        raise ConnectionError("Vector Database connection failed")
    if not chat_db_manager.test_connection():
        raise ConnectionError("Database connection failed")

    # Initialize LLM based on provider
    if llm_provider == "OpenAI":
        llm = OpenAI(
            model="gpt-4",
            temperature=temperature
        )
    else:
        llm = Anthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=temperature
        )

    # Create and run workflow
    workflow = TAGWorkflow(
        vec_db_manager=vec_db_manager,
        chat_db_manager=chat_db_manager,
        llm=llm,
        verbose=True,
        timeout=None  # No timeout for now
    )

    try:
        result = await workflow.run(query=query)
        print(f"Final Result: {result}")
        return result
    except Exception as e:
        print(f"Error running TAG pipeline: {e}")
        return None

def tag_parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='TAG Pipeline CLI')
    parser.add_argument('query', help='Natural language query for the database')
    parser.add_argument('--llm', default='OpenAI', choices=['OpenAI', 'Claude'],
                      help='LLM provider to use (default: OpenAI)')
    parser.add_argument('--temperature', type=float, default=0.1,
                      help='Temperature for LLM (default: 0.1)')

    return parser.parse_args()

async def main():
    os.environ['ENV'] = 'dev'
    args = tag_parse_args()
    try:
        await run_tag_pipeline(args.query, args.llm, args.temperature)
    except Exception as e:
        print(f"Error in RAG main(): {e}")
        return 1
    return 0

if __name__ == "__main__":
    import argparse
    import sys
    import asyncio
    sys.exit(asyncio.run(main()))