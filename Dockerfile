FROM python:3.11-slim

# Install git and gosu (needed for git submodule operations and user switching)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        gosu \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy entrypoint script
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set working directory
WORKDIR /app

# Copy the scaffolder code and templates
COPY scaffolder/ /app/scaffolder/
COPY templates/ /app/templates/

# Set PYTHONPATH so Python can find the scaffolder module
ENV PYTHONPATH=/app

# Use entrypoint to handle user switching
ENTRYPOINT ["/entrypoint.sh"]

# The scaffolder will be run as a Python module
# Users will mount their projects directory and run: python -m scaffolder

