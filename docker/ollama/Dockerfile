FROM ollama/ollama:0.6.8

COPY docker/ollama/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
