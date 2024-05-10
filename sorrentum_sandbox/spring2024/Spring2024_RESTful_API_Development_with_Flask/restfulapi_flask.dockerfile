# Use an official Python runtime as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt & jupyter
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install jupyter

# Expose the Flask port
EXPOSE 5000
EXPOSE 8888

# Define the command to run Flask app
CMD ["bash", "-c", "jupyter notebook --ip='0.0.0.0' --port=8888 --no-browser --allow-root & python app.py"]

