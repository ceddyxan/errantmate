#!/usr/bin/env python3
"""
ErrantMate Startup Script
Automatically handles virtual environment detection and activation
"""

import sys
import os
import subprocess
from pathlib import Path

def find_venv_python():
    """Find the Python executable in the virtual environment."""
    venv_paths = [
        Path("venv/Scripts/python.exe"),  # Windows
        Path("venv/bin/python"),           # Linux/Mac
        Path(".venv/Scripts/python.exe"),  # Windows alternative
        Path(".venv/bin/python"),          # Linux/Mac alternative
    ]
    
    for venv_path in venv_paths:
        if venv_path.exists():
            return str(venv_path)
    return None

def main():
    """Main startup function."""
    print("ErrantMate Application Startup")
    print("=" * 40)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Already in virtual environment")
        run_app()
    else:
        # Try to find and use virtual environment
        venv_python = find_venv_python()
        if venv_python:
            print(f"Found virtual environment: {venv_python}")
            print("Switching to virtual environment...")
            
            # Restart the app using the virtual environment Python
            try:
                subprocess.run([venv_python, "app.py"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to start with virtual environment: {e}")
                print("Falling back to system Python...")
                run_app()
            except KeyboardInterrupt:
                print("\nApplication stopped by user")
        else:
            print("No virtual environment found")
            print("Using system Python")
            run_app()

def run_app():
    """Run the Flask application."""
    try:
        # Import and run the app
        import app
        app.main()
    except ImportError as e:
        print(f"Failed to import app: {e}")
        print("Try installing dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
