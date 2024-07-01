# Specify base image 
FROM python:3.8-slim-buster

# Set working directory to /app
WORKDIR /app

# Copy current directory to /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Listen on port 5000
EXPOSE 5000

# Run app.py
CMD ["python", "app.py"]