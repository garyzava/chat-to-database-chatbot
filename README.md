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
- Intent classification ([Details in Classifier README](./chat2dbchatbot/classifier/README-CLASSIFIER.md))
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
make up
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

1. Go to ```http://localhost:8501 ``` for the main chatbot interface
2. Select your preferred interaction method (RAG, TAG)
3. Choose an LLM provider (OpenAI or Claude)
4. Start asking questions about your database
5. Go to ```http://localhost:3000 ``` for the Langfuse interface when not running on dev mode

## Architecture

- **Frontend**: [Streamlit](https://docs.streamlit.io/)
- **Document Parsing**: [Docling](https://github.com/DS4SD/docling)
- **Vector Database**: [PostgreSQL with pgvector](https://github.com/pgvector/pgvector)
- **Observability**: [Langfuse](https://langfuse.com/docs)
- **LLM Framework**: [LlamaIndex](https://docs.llamaindex.ai/)
- **Container Orchestration**: [Docker Compose](https://docs.docker.com/compose/)

## Paper References

- **RAG (Retrieval-Augmented Generation)**: [Paper by Facebook AI](https://arxiv.org/abs/2005.11401)
- **TAG (Table-Augmented Generation)**: [Paper by UC Berkeley & Stanford University](https://arxiv.org/pdf/2408.14717)


## Data Source Statement

This project uses the Chinook database, a media store database, for development and testing purposes. However, it can be easily adapted for any enterprise or domain-specific use case. 

- **Chinook Database**:
  - **Ownership**: Maintained by [lerocha](https://github.com/lerocha)
  - **Licenses and Use**: The Chinook Database allows use, distribution, and modification without any warranty of any kind.
  - **Access**: Available on GitHub at [https://github.com/lerocha/chinook-database](https://github.com/lerocha/chinook-database)

The intent classifier piece uses data from the following datasets. Access to the data is subject to the respective terms:

- **GretelAI Synthetic Text-to-SQL**:
  - **Ownership**: Gretel.ai
  - **Licenses and Use**: Licensed under the Apache License 2.0, permitting use, distribution, and modification with proper attribution.
  - **Access**: Available on Hugging Face at [https://huggingface.co/datasets/gretelai/synthetic_text_to_sql](https://huggingface.co/datasets/gretelai/synthetic_text_to_sql)

- **Factoid WebQuestions Dataset**:
  - **Ownership**: WebQuestions (http://nlp.stanford.edu/software/sempre/ - Berant et al., 2013, CC-BY)
  - **Licenses and Use**: Distributed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license, allowing sharing and adaptation with appropriate credit.
  - **Access**: Available on GitHub at [https://github.com/brmson/dataset-factoid-webquestions](https://github.com/brmson/dataset-factoid-webquestions)

---

## Evaluation Framework

- Located under the [eval](eval/) sub-folder
- Evaluation Framework [README is here](eval/README.md)