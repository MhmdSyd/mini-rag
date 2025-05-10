APP_NAME='mini-rag'
APP_VERSION="1.0"

FILE_ALLOWED_TYPES=["text/plain", "application/pdf"]
FILE_MAX_SIZE=50
FILE_DEFAULT_CHUNK_SIZE=512000

POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD="postgres_password"
POSTGRES_HOST="pgvector"
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="minirag"

# ================================LLM Config=======================
GENERATION_BACKEND_LITERAL=["OLLAMA", "OPENAI", "COHERE"]
GENERATION_BACKEND="OLLAMA" 

EMBEDDING_BACKEND_LITERAL=["OLLAMA", "OPENAI", "COHERE"]
EMBEDDING_BACKEND="OLLAMA" 

OLLAMA_API_KEY="ollama"
OLLAMA_API_URL="http://ollama:11434/"

OPENAI_API_KEY="sk-proj-mgzZ"
OPENAI_API_URL="https://api.openai.com/v1"

COHERE_API_KEY="2dq2"

GENERATION_MODEL_ID_LITERAL=["gemma2:9b-instruct-q5_0", "gpt-4o-mini", "gpt-3.5-turbo-0125", "command"]
GENERATION_MODEL_ID="gemma2:9b-instruct-q5_0" 

EMBEDDING_MODEL_ID_LITERAL=["mxbai-embed-large:latest", "embed-multilingual-light-v3.0", "text-embedding-3-small"]
EMBEDDING_MODEL_ID="mxbai-embed-large:latest"

EMBEDDING_MODEL_SIZE_LITERAL=[1024, 384, 1536]
EMBEDDING_MODEL_SIZE=1024

INPUT_DAFAULT_MAX_CHARACTERS=1024
GENERATION_DAFAULT_MAX_TOKENS=200
GENERATION_DAFAULT_TEMPERATURE=0.1

# ========================= Vector DB Config =========================
VECTOR_DB_BACKEND_LITERAL=["PGVECTOR", "QDRANT"]
VECTOR_DB_BACKEND="PGVECTOR"
VECTOR_DB_PATH="qdrant_db"

VECTOR_DB_DISTANCE_METHOD_LITERAL=["cosine", "dot"]
VECTOR_DB_DISTANCE_METHOD="cosine"
VECTOR_DB_PGVECTOR_INDEX_THRESHOLD=100

# ========================= Template Configs =========================
PRIMARY_LANG_LITERAL=["en", "ar"]
PRIMARY_LANG = "en"
DEFAULT_LANG = "en"

# ===================Source Code===========================
SOURCE_CODE="https://github.com/MhmdSyd/mini-rag"
