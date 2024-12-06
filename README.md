<p align="center">
  <a href="https://github.com/garyzava/chat-to-database-chatbot">
    <img src="https://media.giphy.com/media/QDjpIL6oNCVZ4qzGs7/giphy.gif" alt="Hippo GIF" height="60"/>
  </a>
</p>
<h1 align="center">Chat2DB GenAI Chatbot</h1>
<p align="center">An LLM-powered chatbot for natural language database queries with extensive observability</p>

<p align="center">
	<a href="#"><img src="https://img.shields.io/badge/Chat2DB-Gen%20AI-8A2BE2" height="20"/></a>
<a href="https://twitter.com/intent/tweet?text=Chat%20to%20your%20Database.%20Chat2DB%20makes%20it%20easy%20to%20deploy%20an%20enterprise-ready%20solution%20using%20an%20LLM-Powered%20chatbot%20and%20explainability%20features.%20https://github.com/garyzava/chat-to-database-chatbot#%20%23opensource%20%23python%20%23genai%20%23llamaindex">
  <img src="https://img.shields.io/badge/tweet--blue?logo=x" alt="Tweet about Chat2DB" />
</a>
</p>

<p align="center">

![](chat2db.webp)

</p><br/>

## Chat to your Database GenAI Chatbot 

A web chatbot interface for database interactions using natural language questions through various interaction methods (RAG, TAG) with different LLMs, including comprehensive observability and tracking.

## Features

- Multiple interaction methods (RAG, TAG)
- LLM provider selection (OpenAI, Claude)
- Intent classification
- Vector search with PGVector
- Langfuse Analytics
- Conversation memory (until browser refresh)
- Docker-based deployment

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- OpenAI API key
- Anthropic API key
- Langfuse account (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/garyzava/chat-to-database-chatbot.git
cd chat-to-database-chatbot
```
2. Configure environment variables:
Copy .env.example to .env and fill in your API keys and configurations.

3. Build and Start the Docker services (one-off)

One-off command:
```bash
make run
```

After the installation, simply run:
```bash
make rup
```

4. Or run the application in developer mode:
```bash
make dev
```

The developer mode installs the streamlit app locally but the databases are still installed on Docker

5. Shut down the application:
```bash
make down
```

## Call the Modules Directly
Running in local mode (make dev), go to the chat2dbchatbot directory. Make sure the virtual enviroment has been activated. Open a new terminal:
```bash
cd chat2dbchatbot
```
Run the RAG utility
```bash
python -m tools.rag "what is the track with the most revenue" --llm OpenAI --temperature 0.1
```
Or run the TAG utility
```bash
python -m tools.tag "what is the track with the most revenue" --llm OpenAI --temperature 0.1
```

## Chatbot Usage

1. Select your preferred interaction method (RAG, TAG)
2. Choose an LLM provider (OpenAI or Claude)
3. Start asking questions about your database

## Architecture

- **Frontend**: [Streamlit](https://docs.streamlit.io/)
- **Document Parsing**: [Docling](https://github.com/DS4SD/docling)
- **Vector Database**: [PostgreSQL with pgvector](https://github.com/pgvector/pgvector)
- **Observability**: [Langfuse](https://langfuse.com/docs)
- **LLM Framework**: [LlamaIndex](https://docs.llamaindex.ai/)
- **Container Orchestration**: [Docker Compose](https://docs.docker.com/compose/)