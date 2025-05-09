#!/bin/bash

echo "Starting Ollama server..."
ollama serve &
SERVE_PID=$!

echo "Waiting for Ollama server to be active..."
while ! ollama list | grep -q 'NAME'; do
  sleep 1
done

# Pull models
ollama pull gemma2:9b-instruct-q5_0
ollama pull mxbai-embed-large:latest

wait $SERVE_PID