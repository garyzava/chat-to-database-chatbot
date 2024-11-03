# Chat to your Database GenAI Chatbot

A web chatbot interface for database interactions using natural language questions through various interaction methods (RAG, TAG, Fine-tuning) with different LLMs, including comprehensive observability and tracking.

## Features

- Multiple interaction methods (RAG, TAG, Fine-tuning)
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
- Anthropic API key (optional)
- Langfuse account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/garyzava/chat-to-database-chatbot.git
cd chat-to-database-chatbot
```
2. Configure environment variables:
Copy .env.example to .env and fill in your API keys and configurations.

3. Build and Start the Docker services (one-off)
```bash
make run
```

4. Run the application:
```bash
make up
```

5. Shut down the application:
```bash
make down
```


## Ingest metadata (TO-DO)

```bash
python ingest.py "doc.pdf"
```


## Chatbot Usage

1. Select your preferred interaction method (RAG, TAG, or Fine-tuning)
2. Choose an LLM provider (OpenAI or Claude)
3. Start asking questions about your database

## Architecture

- **Frontend**: Streamlit
- **Vector Database**: PostgreSQL with pgvector
- **Observability**: MLflow, Langfuse
- **LLM Framework**: LangChain, LlamaIndex
- **Container Orchestration**: Docker Compose
