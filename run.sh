#!/bin/bash

# Create virtual environment

# Activate virtual environment and install requirements
pip install -r requirements.txt

# Execute main.py
python main.py

# Deactivate virtual environment and delete it
deactivate
