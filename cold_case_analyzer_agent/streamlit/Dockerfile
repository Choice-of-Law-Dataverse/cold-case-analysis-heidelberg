# Use official Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY ../requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app code
COPY . .
# Copy docker-entrypoint and make it executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Expose Streamlit port
EXPOSE 8501

# Entrypoint: assemble secrets.toml then run Streamlit
ENTRYPOINT ["/app/docker-entrypoint.sh"]
