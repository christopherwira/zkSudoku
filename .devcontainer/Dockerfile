FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Install ZoKrates using the Bash Script
RUN apt-get update && apt-get install -y curl && \
    # Run the installer script, which will install to /root/.zokrates
    curl -LSfs get.zokrat.es | sh && \
    # As root, move the compiled binary to a shared location in the system's PATH
    mv /root/.zokrates/bin/zokrates /usr/local/bin/zokrates && \
    # Clean up the original installation directory to save space
    rm -rf /root/.zokrates
