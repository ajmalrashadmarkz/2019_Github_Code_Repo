# Use Ubuntu as base image
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1

# Install system dependencies and newer version of meson
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
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --no-cache-dir meson>=0.64.0

# Create odoo user and set up directories
RUN useradd -m -d /opt/odoo -U -r -s /bin/bash odoo \
    && mkdir -p /var/lib/odoo \
    && mkdir -p /var/log/odoo \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo:odoo /var/lib/odoo \
    && chown -R odoo:odoo /var/log/odoo \
    && chown -R odoo:odoo /mnt/extra-addons

# Copy only necessary files first to leverage Docker cache
COPY --chown=odoo:odoo ../requirements.txt /opt/odoo/odoo18_v1/
WORKDIR /opt/odoo/odoo18_v1

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY --chown=odoo:odoo ../ /opt/odoo/odoo18_v1

# Set up proper permissions
RUN chown -R odoo:odoo /opt/odoo

# Switch to odoo user
USER odoo

# Expose Odoo ports
EXPOSE 8069 8072

# Set default command
CMD ["./odoo-bin", "-c", "/opt/odoo/odoo18_v1/odoo.conf"]