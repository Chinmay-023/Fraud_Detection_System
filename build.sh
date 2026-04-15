#!/bin/bash

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Train models
python model_training.py

# Initialize database
python -c "from app import init_database; init_database()"
