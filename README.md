# mini-rag

This is a minimal implementation for the RAG question answering based on documents.

# Requirments:

a. python 3.8 or later

b. Download and install MiniConda

c.  Create a new environment using following command:

```bash
$ conda create -n mini-rang python=3.8
```
d. Activate the environment:
```bash
$ conda activate mini-rag
```

## Install requirements packages
```bash
$ pip install -r requirements.txt
```

## Rename .env.example to .env and set all required variable.

## RUN FastAPI app:

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 8080
```