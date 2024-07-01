#!/bin/bash

# Build the Docker image
docker build -t hadoop-streaming .

# # Run the Docker container and start an interactive shell session
docker run --rm -v "$(pwd)/data/input.txt:/usr/local/hadoop/input.txt" hadoop-streaming
