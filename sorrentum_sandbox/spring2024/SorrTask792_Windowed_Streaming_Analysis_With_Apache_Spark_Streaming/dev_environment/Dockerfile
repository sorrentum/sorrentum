# Use the jupyter/pyspark-notebook as the base image
FROM jupyter/pyspark-notebook:latest

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install additional necessary packages
RUN pip install --no-cache-dir \
    scikit-learn \
    pandas \
    matplotlib

# Expose the port Jupyter Notebook runs on
EXPOSE 8888

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

# Expose the port Jupyter Notebook runs on
EXPOSE 8888

# Start Jupyter Notebook with PySpark
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]