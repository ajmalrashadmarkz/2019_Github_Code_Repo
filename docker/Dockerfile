# Use Ubuntu as base image
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables for better logging and performance
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    # Add virtual environment path to PATH
    VIRTUAL_ENV=/opt/odoo/venv \
    PATH="/opt/odoo/venv/bin:$PATH"

# Create odoo user with specific UID/GID for better permission management
RUN groupadd -g 1000 odoo && \
    useradd -u 1000 -g odoo -d /opt/odoo -m -s /bin/bash odoo

# Install system dependencies with optimized layer and cleanup
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-wheel \
    python3-setuptools \
    nodejs \
    npm \
    git \
    postgresql-client \
    libpq-dev \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libevent-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    fonts-liberation \
    gdebi-core \
    wget \
    ninja-build \
    libcairo2-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

# Set up directories with proper permissions
RUN mkdir -p /var/lib/odoo \
    /var/log/odoo \
    /mnt/extra-addons \
    /opt/odoo/odoo18_v1 \
    && chown -R odoo:odoo /var/lib/odoo \
    /var/log/odoo \
    /mnt/extra-addons \
    /opt/odoo

# Switch to odoo user for creating virtual environment
USER odoo

# Create and activate virtual environment
RUN python3 -m venv $VIRTUAL_ENV

# Set working directory
WORKDIR /opt/odoo/odoo18_v1

# Copy requirements first for better cache utilization
COPY --chown=odoo:odoo requirements.txt ./

# Install Python dependencies in virtual environment
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir python-json-logger \
    && pip install --no-cache-dir meson>=0.64.0

# Copy application code
COPY --chown=odoo:odoo . .

# Create directory for custom logging config
RUN mkdir -p logging

# Add a startup script
COPY --chown=odoo:odoo docker/scripts/docker-entrypoint.sh /opt/odoo/
RUN chmod +x /opt/odoo/docker-entrypoint.sh

# Expose Odoo ports
EXPOSE 8069 8072

ENTRYPOINT ["/opt/odoo/docker-entrypoint.sh"]
CMD ["./odoo-bin"]
