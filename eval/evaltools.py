import re
from difflib import SequenceMatcher
import sqlfluff

import sys
import os
project_dir = os.path.abspath("..") 
chat2dbchatbot_dir = os.path.join(project_dir, "chat2dbchatbot")
if chat2dbchatbot_dir not in sys.path:
    sys.path.append(chat2dbchatbot_dir)
from tools.tagsql import run_tag_pipeline
from tools.ragsql import run_rag_pipeline

from sqltr import SQLTestRun
sqlTestRun = SQLTestRun()

def gen_rag_query(textQuery: str, llm_provider: str = "OpenAI", temperature: float = 0.1)->str:
        result = ""
        try:
            result = run_rag_pipeline(textQuery, llm_provider, temperature)
            return result
        except Exception as e:
            return "error"
        
async def gen_tag_query(textQuery: str, llm_provider: str = "OpenAI", temperature: float = 0.1)->str:
        result = ""
        try:
            result = await run_tag_pipeline(textQuery, llm_provider, temperature, "query_synthesis")
            return result
        except Exception as e:
            return "error"

def check_sql_errors(rq: str)->dict:
    try:
        # Create a config for the specific dialect
        config = sqlfluff.Config(overrides={"dialect": 'postgres'})

        # Parse the SQL query
        parsed = sqlfluff.parse(rq, config=config)
        
        # Check for parsing issues
        if not parsed:
            return {"status": "invalid", "numIssues": "N/A"}

        # Lint the SQL query
        lint_results = sqlfluff.lint(rq, config=config)

        # Format linting results
        issues = [
            {
                "line_no": issue.line_no,
                "code": issue.code,
                "description": issue.description,
            }
            for issue in lint_results
        ]

        # Return the validation results
        if issues:
            return {
                "status": "valid",
                "numIssues": len(issues),
            }
        else:
            return {
                "status": "valid",
                "numIssues": 0,
            }
    except Exception as e:
        return {"status": "invalid", "numIssues": "N/A"}

def is_sql_check(rq: str) -> bool:
    isSQL = False
    rq  = rq.strip().upper()
    if (rq and (rq != "ERROR") and (rq.startswith('SELECT') or rq.startswith('WITH') or rq.startswith('CREATE TABLE'))):
            isSQL = True
    return isSQL

def confirm_type(rq: str, isExpectSQL:bool) -> bool:
    if is_sql_check(rq) == isExpectSQL:
         return True
    else: return False