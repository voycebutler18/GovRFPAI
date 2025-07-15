#!/bin/bash

# Set default port if not provided
PORT=${PORT:-5000}

# Start gunicorn with the correct port
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 30 app:app
