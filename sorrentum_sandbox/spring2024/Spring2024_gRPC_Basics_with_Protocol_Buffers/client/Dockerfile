# set base image
FROM python:3.8-slim

# set work space
WORKDIR /app

# Copy the required files into the container
COPY server.py ./

# install dependence
RUN pip install --no-cache-dir \
    grpcio \
    grpcio--tools

# start service
CMD ["python", "client.py"]
