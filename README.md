# mini-rag

This is a minimal implementation for the RAG question answering based on documents.


## Requirements

- Python 3.8 or later

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

### (Optional) Setup you command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## For documented end-points using Swagger:

```bash
$ http://127.0.0.1:8080/docs
```

## Run Docker Compose Service:

```bash
$ cd docker
$ cp .env.example .env
```

- Update `.env` with your credentials.

## Installing mongoDB docker service:

```bash
$ docker-compose -f 'docker compose filename.yml' up -d --build
```


