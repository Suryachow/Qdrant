
@echo off
echo Starting Qdrant Docker Container...
docker pull qdrant/qdrant
docker run -d -p 6333:6333 -v "%~dp0qdrant_storage":/qdrant/storage --name local_qdrant qdrant/qdrant
echo Qdrant is running on http://localhost:6333
pause
