# syntax = docker/dockerfile:experimental

FROM ubuntu:20.04 AS builder

## Install dependencies
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    wget \
#    git \
#    python3 \
#    python3-pip \
#    build-essential \
#    libblas-dev \
#    liblapack-dev \
#    libatlas-base-dev \
#    gfortran \
#    libatlas3-base \
#    libumfpack5 \
#    libopenblas-dev \
#    libdsdp-dev \
#    libfftw3-dev \
#    libglpk-dev \
#    libgsl-dev \
#    libgcc-10-dev \
#    && wget http://faculty.cse.tamu.edu/davis/SuiteSparse/SuiteSparse-4.5.3.tar.gz \
#    && tar -xf SuiteSparse-4.5.3.tar.gz \
#    && export CVXOPT_SUITESPARSE_SRC_DIR=$(pwd)/SuiteSparse \
#    && export CPPFLAGS="-I/usr/include/suitesparse" \
#    && export CVXOPT_BUILD_FFTW=1 
#
#
#ENV DEBIAN_FRONTEND=noninteractive

# Name of the virtual environment to create.
ENV ENV_NAME="venv"
ENV APP_DIR=/app
ENV HOME=/home

# Where to copy the installation files.
ENV INSTALL_DIR=/install
WORKDIR $INSTALL_DIR

# Clean up the installation.
# To disable the clean up stage, comment out the variable, instead of setting
# to False.
#ENV CLEAN_UP_INSTALLATION=True

# - Install OS packages.
COPY devops/docker_build/install_os_packages.sh .
RUN /bin/bash -c "./install_os_packages.sh"

# - Install Python packages.
# Copy the minimum amount of files needed to call install_requirements.sh so we
# can cache it effectively.
COPY devops/docker_build/poetry.lock .
COPY devops/docker_build/poetry.toml .
COPY devops/docker_build/pyproject.toml .
COPY devops/docker_build/install_python_packages.sh .
RUN /bin/bash -c "./install_python_packages.sh"

# - Install Jupyter extensions.
COPY devops/docker_build/install_jupyter_extensions.sh .
RUN /bin/sh -c "./install_jupyter_extensions.sh"

# - Install Docker-in-docker.
# TODO(gp): @samarth enable this and debug.
#COPY devops/docker_build/install_dind.sh .
#RUN /bin/bash -c "./install_dind.sh"

# - Create users and set permissions.
COPY devops/docker_build/create_users.sh .
RUN /bin/bash -c "./create_users.sh"
COPY devops/docker_build/etc_sudoers /etc/sudoers

# Mount external filesystems.
# RUN mkdir -p /s3/alphamatic-data
# RUN mkdir -p /fsx/research

COPY devops/docker_run/bashrc $HOME/.bashrc

# Pass the container version (e.g., `1.0.0`) to the environment.
ARG AM_CONTAINER_VERSION
ENV AM_CONTAINER_VERSION=$AM_CONTAINER_VERSION
RUN echo "AM_CONTAINER_VERSION=$AM_CONTAINER_VERSION"

# TODO(gp): Is this needed?
WORKDIR $APP_DIR

ENTRYPOINT ["devops/docker_run/entrypoint.sh"]
