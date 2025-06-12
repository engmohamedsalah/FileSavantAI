#!/bin/bash

# This script rebuilds the Docker image and then runs a new container from it.
# It passes any arguments it receives directly to the container's command.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "➡️  Rebuilding Docker image: filesavantai"
docker build -t filesavantai .

echo "🚀  Running new container..."
# Pass all script arguments ($@) to the docker run command
# Also mount the local sample_data directory to /data inside the container
docker run --rm -v "$(pwd)/.env:/app/.env" -v "$(pwd)/sample_data:/data" filesavantai "$@" 

#docker run --rm -v "$(pwd)/.env:/app/.env" filesavantai "$@" 