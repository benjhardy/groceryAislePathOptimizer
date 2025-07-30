#!/bin/bash

echo "Setting up Grocery Route Optimizer..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if Chrome/Chromium is installed for Selenium
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "Warning: Chrome or Chromium is required for web scraping features."
    echo "Please install Chrome from: https://www.google.com/chrome/"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "2. Run the application:"
echo "   python main.py"
echo ""
echo "To run tests:"
echo "   python test_app.py"