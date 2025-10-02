#!/usr/bin/env bash
# Render start script for backend

cd backend
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
