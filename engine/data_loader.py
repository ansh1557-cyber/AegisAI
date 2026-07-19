"""
Aegis AI
Module: Data Loader
Version: 0.0.1
"""

import pandas as pd


class DataLoader:

    def load_csv(self, file_path):
        df = pd.read_csv(file_path)

        # Ensure standard column names
        df.columns = [col.strip() for col in df.columns]

        return df