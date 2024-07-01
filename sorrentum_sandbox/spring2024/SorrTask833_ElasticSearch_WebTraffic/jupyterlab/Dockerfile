FROM python:3.9

# Update and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install JupyterLab
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app's source code
COPY . /app

# Expose the port Jupyter will run on
EXPOSE 8888

# Run JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]

