#!/bin/bash

# Django Course Platform Setup Script
# This script sets up a Django application with nginx and MySQL support

set -e  # Exit on any error

echo "Starting Django Course Platform setup..."

# Update system packages

echo "Updating system packages..."

sudo apt-get update -y

# Install system dependencies

echo "Installing system dependencies..."
sudo apt install -y \
    nginx \
    pkg-config \
    libmysqlclient-dev \
    default-libmysqlclient-dev \
    build-essential \
    python3.12-venv \
    python3-pip \
    git

# Clone the course platform repository

echo "Cloning course platform repository..."

if [ ! -d "course_platform" ]; then
    git clone https://github.com/shvpn/course_platform.git
    sudo mv course_platform /home/ubuntu/
fi

# Create and activate virtual environment

echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies

echo "Installing Python packages..."
pip install --upgrade pip
pip install Django mysqlclient pillow

# Run setup scripts if they exist

echo "Running setup scripts..."
if [ -f "/home/ubuntu/course_platform/update_settings.sh" ]; then
    sudo bash /home/ubuntu/course_platform/update_settings.sh
fi

if [ -f "/home/ubuntu/course_platform/nginx_setup.sh" ]; then
    sudo bash /home/ubuntu/course_platform/nginx_setup.sh
fi

# Change to the Django project directory

echo "Changing to Django project directory..."
if [ -d "/home/ubuntu/Test-cloud" ]; then
    cd /home/ubuntu/Test-cloud/
elif [ -d "/home/ubuntu/course_platform" ]; then
    cd /home/ubuntu/course_platform/
else
    echo "Warning: Could not find Django project directory"
    echo "Available directories:"
    ls -la
    exit 1
fi

# Run Django migrations (if manage.py exists)

if [ -f "/home/ubuntu/course_platform/manage.py" ]; then
    echo "Running Django migrations..."
    python /home/ubuntu/course_platform/manage.py migrate --noinput || echo "Migration failed or not needed"
    
    echo "Collecting static files..."
    python /home/ubuntu/course_platform/manage.py collectstatic --noinput || echo "Static files collection failed or not needed"
    
    echo "Setup complete! Starting development server..."
    echo "Access your application at: http://localhost:8000"
    python /home/ubuntu/course_platform/manage.py runserver 0.0.0.0:80
else
    echo "Error: manage.py not found in current directory"
    echo "Current directory contents:"
    ls -la
fi
