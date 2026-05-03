"""
XONOMO Anti-Detect Browser
Main entry point for the application.

Launch with: python main.py
"""

import sys
import os


def main():
    # Ensure the working directory is the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Import and run GUI
    from gui_app import run_app
    run_app()


if __name__ == "__main__":
    main()
