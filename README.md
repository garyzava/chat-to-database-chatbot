# Chat to your Database GenAI Chatbot

A web chatbot interface for database interactions using natural language questions through various interaction methods (RAG, TAG) with different LLMs, including comprehensive observability and tracking.

## Features

- Multiple interaction methods (RAG, TAG)
- LLM provider selection (OpenAI, Claude)
- Intent classification
- Vector search with PGVector
- MLFlow tracking
- Langfuse analytics
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

## Ingest metadata (TO-DO)

```bash
python ingest.py "doc.pdf"
```

## Call the Modules Directly
Running in local mode (make dev), go to the chat2dbchatbot directory
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

- **Frontend**: Streamlit
- **Vector Database**: PostgreSQL with pgvector
- **Observability**: MLflow, Langfuse
- **LLM Framework**: LangChain, LlamaIndex
- **Container Orchestration**: Docker Compose
