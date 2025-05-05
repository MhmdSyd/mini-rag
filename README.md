# mini-rag

**mini-rag** is a minimal yet powerful Retrieval-Augmented Generation (RAG) system built using FastAPI. It allows users to chat with a Large Language Model (LLM) using their own documents as contextual knowledge. This system supports multiple LLM backends and integrates MongoDB and Qdrant to manage and retrieve documents efficiently.

---

## 🧰 Tech Stack

- **FastAPI** – Backend API framework
- **MongoDB** – Stores uploaded files, chunked documents, and metadata
- **Docker** – Manages MongoDB service.
- **Qdrant** – Vector database for semantic search of document chunks
- **LLMs Supported**:
  - OpenAI (GPT)
  - Cohere
  - Ollama (local models)

---

## ⚙️ Features

- 📁 Upload and store custom documents
- ✂️ Automatically chunk and embed documents
- 🧠 Chat with LLMs using relevant document context (RAG)
- 🔍 Semantic search with Qdrant
- 🔄 Multiple LLM provider support
- 📑 API documentation available via Swagger UI: [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)

---

## Requirements

- Python 3.8 or later


#### Install Dependencies

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

#### Install Python using MiniConda

1) Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag python=3.8
```
3) Activate the environment:
```bash
$ conda activate mini-rag
```

#### (Optional) Setup you command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/MhmdSyd/mini-rag.git
cd mini-rag
```

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.


### Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### For documented endpoints using Swagger:

```bash
$ http://127.0.0.1:5000/docs
```

### Run Docker Compose Service:

```bash
$ cd docker
$ cp .env.example .env
```

- Update `.env` with your credentials.

### Install MongoDB docker service:

```bash
$ cd docker
$ docker compose up --build # --build use it once at the first time.
# use -d to run docker service in background 
```




