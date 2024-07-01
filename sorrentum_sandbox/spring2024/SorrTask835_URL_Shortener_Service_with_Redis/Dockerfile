# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN apt-get update && apt-get install -y redis-server

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8080

# Run Redis server and Streamlit app.
CMD redis-server --daemonize yes && flask run --host=0.0.0.0 --port=8080
