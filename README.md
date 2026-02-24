# LangGraph Chatbot (Streamlit)

A chat application with **multi-threaded conversations**, powered by **LangGraph** and **Hugging Face Qwen**, with a **Streamlit** frontend.

## Architecture

| Component | Description |
|-----------|-------------|
| **Frontend** | `streamlit_frontend_threading.py` — Streamlit UI with sidebar, chat threads, and streaming responses |
| **Backend** | `langgraph_backend.py` — LangGraph state graph with in-memory checkpointer and Qwen (Hugging Face) as the LLM |

- **LLM**: Qwen2-7B-Instruct via Hugging Face Inference API (`langchain-huggingface`).
- **State**: Conversation history is stored per thread using LangGraph’s `InMemorySaver` checkpointer.
- **Streaming**: Assistant replies stream token-by-token in the UI.

## Prerequisites

- **Python 3.12+**
- **Hugging Face API token** — [Create one](https://huggingface.co/settings/tokens) and set `HUGGINGFACEHUB_API_TOKEN` (see below).

## Environment Variables

Create a `.env` file in the project root (or export in your shell):

```bash
# Required for Hugging Face Inference API (Qwen)
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
```

## Local Setup

```bash
# Clone (if needed) and enter project
cd chatbot_streamlit

# Create virtual environment (optional)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python -m streamlit run streamlit_frontend_threading.py --server.port=8501
```

Open **http://localhost:8501** in your browser.

## Docker

### Build and run with Docker

```bash
# Build image
docker build -t chatbot_streamlit .

# Run container (ensure .env or HUGGINGFACEHUB_API_TOKEN is set)
docker run -p 8501:8501 --env-file .env chatbot_streamlit
```

### Run with Docker Compose

```bash
docker-compose up --build
```

- **Streamlit**: http://localhost:8501  
- The compose file mounts the current directory into the container (`.:/app`) so you can edit code and see changes after restarting.
- Port `11434` is mapped for optional use (e.g. a separate Ollama service); the app itself uses Hugging Face Qwen.

**Compose snippet** (from `docker-compose.yaml`):

- **Service**: `chatbot` (image built from project `Dockerfile`)
- **Ports**: `8501` (Streamlit), `11434` (optional, e.g. Ollama)
- **Volumes**: `.:/app` for live code updates
- **Command**: runs `streamlit run streamlit_frontend_threading.py` with port 8501 and bind to `0.0.0.0`

To use the Hugging Face token in Compose, add to `docker-compose.yaml` under `environment` or use an `.env` file and `env_file: .env` in the service.

## Features

- **New chat** — Sidebar “New Chat” starts a new thread; optional “New Chat Name” labels it.
- **Thread list** — “My Conversations” lists threads; click one to load its history.
- **Streaming** — Assistant messages stream in real time.
- **Thread persistence** — Per-thread history is kept in memory for the session (LangGraph checkpointer).

## Project Layout

```
.
├── streamlit_frontend_threading.py   # Streamlit UI and thread handling
├── langgraph_backend.py              # LangGraph graph + Qwen LLM
├── requirements.txt
├── Dockerfile                        # Python 3.12 slim, Streamlit on 8501
├── docker-compose.yaml               # Single service: build + run frontend
└── README.md
```

## Dockerfile Summary

- **Base**: `python:3.12-slim`
- **System deps**: build tools and libs for Pillow/crypto (e.g. `libjpeg-dev`, `zlib1g-dev`, `libffi-dev`, `git`, `curl`).
- **App**: copies `requirements.txt`, installs dependencies and Streamlit, copies app code, exposes **8501**.
- **CMD**: `streamlit run streamlit_frontend_threading.py --server.port=8501 --server.address=0.0.0.0`.

## Changing the model

Edit `langgraph_backend.py`: update `repo_id` in `HuggingFaceEndpoint` (e.g. `Qwen/Qwen2-7B-Instruct`) or switch to a local pipeline (e.g. `HuggingFacePipeline`) if you run models on your own machine.
