#!/usr/bin/env python3
"""Evaluate the trip duration model on validation and test sets."""

import os
import sys

# Run from project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.evaluate import load_and_evaluate

DATA_DIR = os.path.join(ROOT, "data")
MODEL_PATH = os.path.join(ROOT, "models", "model.pkl")
if not os.path.isfile(MODEL_PATH):
    MODEL_PATH = os.path.join(ROOT, "model.pkl")

if __name__ == "__main__":
    val_path = os.path.join(DATA_DIR, "val.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    if not os.path.isfile(MODEL_PATH):
        print(f"Model not found: {MODEL_PATH}")
        sys.exit(1)
    if not os.path.isfile(val_path) or not os.path.isfile(test_path):
        print(f"Data not found in {DATA_DIR}. Ensure val.csv and test.csv exist.")
        sys.exit(1)
    load_and_evaluate(val_path, test_path, MODEL_PATH)
