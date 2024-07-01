# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Flask, Jupyter Notebook, and Redis
RUN apt-get update && \
    apt-get install -y redis-server && \
    pip install Flask jupyter redis

# Expose the ports Flask, Jupyter Notebook, and Redis are running on
EXPOSE 5000 8888 6379

# Set up Jupyter configuration
RUN jupyter notebook --generate-config && \
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py

# Command to run the Flask application, Jupyter Notebook, and Redis
CMD ["bash", "-c", "service redis-server start && python app.py & jupyter notebook --ip 0.0.0.0 --no-browser --allow-root"]
