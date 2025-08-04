FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set Python Path to our root directory
ENV PYTHONPATH="${PYTHONPATH}:/workspaces/zkSudoku"

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Install ZoKrates using the Bash Script
RUN apt-get update && apt-get install -y curl && \
    # Run the installer script, which will install to /root/.zokrates
    curl -LSfs get.zokrat.es | sh && \
    # Move the entire installation to a shared location for optional software
    mv /root/.zokrates /opt/zokrates

# Use the ENV instruction to permanently add the ZoKrates bin directory to the PATH.
# This makes the 'zokrates' command available to all users.
ENV PATH="/opt/zokrates/bin:${PATH}"
