import tools.tag

#customized inject for evaluation framework (note still calling chatbot folder tag file for some functions)

#Run TAG to directly get SQL without last step where response is changed to nature language answers
async def run_tag_pipeline(query: str, llm_provider: str = "OpenAI", temperature: float = 0.1
                           ,up_to: str = "query_synthesis") -> str:
    """Run the TAG pipeline with given parameters"""
    # Database setup 
    from tools.db import DatabaseManager
    vec_db_manager = DatabaseManager(db_type='vecdb')
    chat_db_manager = DatabaseManager(db_type='db')

    
    #check if DB connection successful
    if not vec_db_manager.test_connection():
        raise ConnectionError("Vector Database connection failed")
    if not chat_db_manager.test_connection():
        raise ConnectionError("Database connection failed")

    # Initialize LLM based on provider
    if llm_provider == "OpenAI":
        llm = tools.tag.OpenAI(
            model="gpt-4",
            temperature=temperature
        )
    else:
        llm = tools.tag.Anthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=temperature
        )

    # Create and run workflow
    workflow = tools.tag.TAGWorkflow(
        vec_db_manager=vec_db_manager,
        chat_db_manager=chat_db_manager,
        llm=llm,
        verbose=True,
        timeout=None  # No timeout for now
    )
    
    try:
        if up_to == "query_synthesis":
            event = await workflow.query_synthesis(
                tools.tag.Context(workflow), 
                tools.tag.StartEvent(query=query)
            )
            if isinstance(event, tools.tag.QuerySynthesisEvent):
                return event.sql_query  # Return the SQL query
            else:
                return event.result  # Return error or stop message
        else:
            result = await workflow.run(query=query)
            return result
    except Exception as e:
        print(f"Error running TAG pipeline: {e}")
        return None