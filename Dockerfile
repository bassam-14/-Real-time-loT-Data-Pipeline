# Dockerfile for Airflow with custom dependencies
# Extends the official Apache Airflow image with additional packages

FROM apache/airflow:3.1.0

# Switch to root user to install system dependencies if needed
USER root

# Install any system-level dependencies (optional)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Set working directory
WORKDIR /opt/airflow
