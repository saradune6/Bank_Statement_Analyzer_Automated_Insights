# utils.py
import pandas as pd

def parse_csv(uploaded_file):
    return pd.read_csv(uploaded_file)
