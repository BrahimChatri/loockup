#!/bin/bash

# Exit on errors
set -e

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements if requirements.txt exists, else install basics
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    pip install flask
fi

# Run your app
python main.py
