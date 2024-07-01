FROM python:3.9

# Install Redis server.
RUN apt-get update && apt-get install -y redis-server

# Set up working directory.
WORKDIR /app

# Copy requirements file.
COPY requirements.txt /app

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files.
COPY . /app

# Expose the port where Streamlit app will run.
EXPOSE 8501

# Run Redis server and Streamlit app.
CMD redis-server --daemonize yes && streamlit run Users_dashboard.py