FROM python:3.9

# Install Package Updates and the PostgreSQL client.
RUN apt-get update -yqq && \
	apt-get install -y \
	postgresql-client

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Jupyter Notebook runs on.
EXPOSE 8888