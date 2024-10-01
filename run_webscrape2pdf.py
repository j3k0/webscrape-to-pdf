#!/usr/bin/env python3

import sys
import os

# Add the parent directory to the Python path
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

try:
    from webscrape2pdf.main import main
    if __name__ == "__main__":
        sys.exit(main())
except ImportError as e:
    print(f"Error importing module: {e}")
    print("Please make sure all required dependencies are installed.")
    print("You can install them using: pip install -r requirements.txt")
    sys.exit(1)