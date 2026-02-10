# Use Python 3 base image
FROM python:3.12-alpine3.20

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    bash \
    curl \
    wget \
    gawk \
    gzip \
    tar \
    grep \
    sed

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all scripts
RUN mkdir -p /scripts
COPY scripts/ /scripts

# Make all scripts executable
RUN chmod +x /scripts/*

# Add scripts directory to PATH
ENV PATH="/scripts:${PATH}"

# Set default command
CMD ["/bin/sh"]
