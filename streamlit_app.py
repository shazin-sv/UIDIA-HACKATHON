import sys
import os

# Add current directory to path so imports work correctly
sys.path.append(os.path.dirname(__file__))

from dashboard.app import main

if __name__ == "__main__":
    main()
