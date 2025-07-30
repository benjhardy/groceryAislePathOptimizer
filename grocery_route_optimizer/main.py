#!/usr/bin/env python3
"""
Grocery Route Optimizer - Main Application
A proof of concept for optimizing shopping routes in grocery stores
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from src.app import GroceryRouteApp


def main():
    """Main entry point for the application"""
    app = GroceryRouteApp()
    app.run()


if __name__ == "__main__":
    main()