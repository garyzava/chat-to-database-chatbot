# Chat Database GenAI Chatbot

A streamlined chatbot interface for database interactions using various LLM methods (RAG, TAG, Fine-tuning) with comprehensive observability and tracking.

## Features

- Multiple interaction methods (RAG, TAG, Fine-tuning)
- LLM provider selection (OpenAI, Claude)
- Intent classification
- Vector search with PGVector
- MLFlow tracking
- Langfuse analytics
- Conversation memory
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
git clone https://github.com/yourusername/chat-database.git
cd chat-database
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Copy .env.example to .env and fill in your API keys and configurations.

5. Start the Docker services:
```bash
docker-compose up -d
```

6. Ingest metadata:
```bash
python ingest.py
```

7. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Select your preferred interaction method (RAG, TAG, or Fine-tuning)
2. Choose an LLM provider (OpenAI or Claude)
3. Start asking questions about your database

## Architecture

- **Frontend**: Streamlit
- **Vector Database**: PostgreSQL with pgvector
- **Observability**: MLflow, Langfuse
- **LLM Framework**: LangChain, LangGraph
- **Container Orchestration**: Docker Compose

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.