#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script untuk menjalankan aplikasi backend dengan beban yang lebih ringan,
memanfaatkan model ML yang sudah dilatih dan disimpan sebelumnya.
"""

import os
from app import create_app

# Check if models directory exists
if not os.path.exists('models'):
    print("WARNING: Models directory not found. Please run train_models.py first.")
    os.makedirs('models', exist_ok=True)

# Check if models exist
model_path = 'models/tfidf_vectorizer.joblib'
if not os.path.exists(model_path):
    print(f"WARNING: Model file {model_path} not found. Models will be created on first use.")

# Create app
app = create_app()

if __name__ == '__main__':
    print("\n=== RUNNING LIGHTWEIGHT BACKEND ===")
    print("Using pre-trained ML models for better performance")
    print("If this is the first run, models will be created automatically")
    print("For best performance, run train_models.py first\n")
    
    # Print routes
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.methods} {rule.rule}")
    print("========================\n")
    
    # Run app
    app.run(debug=True) 