ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base
# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1
# Set the working directory in the container.
WORKDIR /app
# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --no-cache-dir -r requirements.txt
# Set the environment variable for Hugging Face Home directory.
ENV HF_HOME /app/huggingface_home
# Set permissions for the huggingface_home directory.
RUN mkdir -p /app/huggingface_home \
    && chown -R appuser:appuser /app/huggingface_home \
    && chmod -R 755 /app/huggingface_home
# Switch to the non-privileged user to run the application.
USER appuser
COPY . .
# Expose the port that the application listens on.
EXPOSE 8000
CMD python app.py
