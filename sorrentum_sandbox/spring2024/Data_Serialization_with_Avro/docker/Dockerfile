# Use an official base image
FROM jupyter/base-notebook:latest

# Set the working directory in the container
WORKDIR /home/jovyan/work

# Install pandas and avro
RUN pip install pandas avro-python3

# Copy all the files to the working directory
COPY . .

# Expose port 8888 for Jupyter notebook
EXPOSE 8888

# Run Jupyter notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token='Avro'"]