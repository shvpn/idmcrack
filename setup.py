#!/usr/bin/env python3
"""
Django Course Platform Setup Script
This script sets up a Django application with nginx and MySQL support
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, check=True, shell=True):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=check, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def print_step(message):
    """Print a step message"""
    print(f"\n{'='*50}")
    print(message)
    print('='*50)

def main():
    """Main setup function"""
    print_step("Starting Django Course Platform setup...")
    
    # Update system packages
    print_step("Updating system packages...")
    run_command("sudo apt update -y")
    
    # Install system dependencies
    print_step("Installing system dependencies...")
    packages = [
        "nginx",
        "pkg-config", 
        "libmysqlclient-dev",
        "default-libmysqlclient-dev",
        "build-essential",
        "python3.12-venv",
        "python3-pip",
        "git"
    ]
    
    install_cmd = f"sudo apt install -y {' '.join(packages)}"
    run_command(install_cmd)
    
    # Clone the course platform repository
    print_step("Cloning course platform repository...")
    if not Path("course_platform").exists():
        run_command("git clone https://github.com/shvpn/course_platform.git")
    else:
        print("Repository already exists, skipping clone...")
    
    # Create and activate virtual environment
    print_step("Setting up Python virtual environment...")
    if not Path("venv").exists():
        run_command("python3 -m venv venv")
    
    # Get the virtual environment python and pip paths
    venv_python = Path("venv/bin/python").absolute()
    venv_pip = Path("venv/bin/pip").absolute()
    
    if not venv_python.exists():
        print("Error: Virtual environment not created properly")
        sys.exit(1)
    
    # Install Python dependencies
    print_step("Installing Python packages...")
    run_command(f"{venv_pip} install --upgrade pip")
    
    python_packages = ["Django", "mysqlclient", "pillow"]
    for package in python_packages:
        run_command(f"{venv_pip} install {package}")
    
    # Run setup scripts if they exist
    print_step("Running setup scripts...")
    
    update_script = Path("course_platform/update_settings.sh")
    if update_script.exists():
        run_command(f"sudo bash {update_script}")
    else:
        print("update_settings.sh not found, skipping...")
    
    nginx_script = Path("course_platform/nginx_setup.sh")
    if nginx_script.exists():
        run_command(f"sudo bash {nginx_script}")
    else:
        print("nginx_setup.sh not found, skipping...")
    
    # Change to the Django project directory
    print_step("Changing to Django project directory...")
    
    django_dir = None
    possible_dirs = ["Test-cloud", "course_platform"]
    
    for dir_name in possible_dirs:
        if Path(dir_name).exists():
            django_dir = Path(dir_name)
            break
    
    if not django_dir:
        print("Warning: Could not find Django project directory")
        print("Available directories:")
        for item in Path(".").iterdir():
            if item.is_dir():
                print(f"  {item.name}")
        sys.exit(1)
    
    # Change to Django directory
    os.chdir(django_dir)
    print(f"Changed to directory: {django_dir.absolute()}")
    
    # Run Django migrations (if manage.py exists)
    manage_py = Path("manage.py")
    if manage_py.exists():
        print_step("Running Django setup...")
        
        # Run migrations
        print("Running Django migrations...")
        result = run_command(f"{venv_python} manage.py migrate --noinput", check=False)
        if result.returncode != 0:
            print("Migration failed or not needed")
        
        # Collect static files
        print("Collecting static files...")
        result = run_command(f"{venv_python} manage.py collectstatic --noinput", check=False)
        if result.returncode != 0:
            print("Static files collection failed or not needed")
        
        # Start development server
        print_step("Setup complete! Starting development server...")
        print("Access your application at: http://localhost:8000")
        print("Press Ctrl+C to stop the server")
        
        try:
            run_command(f"{venv_python} manage.py runserver 0.0.0.0:8000")
        except KeyboardInterrupt:
            print("\nServer stopped by user")
            sys.exit(0)
    else:
        print("Error: manage.py not found in current directory")
        print("Current directory contents:")
        for item in Path(".").iterdir():
            print(f"  {item.name}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
