from typing import List

from main.config import API_KEY_OPENAI
from  openai import OpenAI
import os
import numpy as np
import pandas as pd
import time

import os
from io import StringIO
from datetime import datetime
import hashlib
from collections import defaultdict

if API_KEY_OPENAI:
    client = OpenAI(
        api_key = API_KEY_OPENAI,
    )

    def get_completion(prompt, model="gpt-4o-mini", temperature=0):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response


def parse_response_table(
        content: str, 
        ffill_cols: List[str] = None,
        date_col: List[str] = None
        ) -> pd.DataFrame:
    '''
    Parse the table response from OpenAI into a pandas DataFrame
    '''
    # Using StringIO to treat the text as a file-like object for pandas
    data = StringIO(content)

    # Read the table into a pandas DataFrame
    df = pd.read_csv(data, delimiter='|',  engine='python')

    # Cleaning the DataFrame by stripping leading/trailing whitespaces from column names and data
    df.columns = df.columns.str.strip()
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    df = df[[col for col in df if 'Unnamed' not in col]]

    # Remove rows with dashes
    col_name = df.select_dtypes(include=['object']).columns[0]
    df = df.loc[~df[col_name].fillna('').str.contains('--')]

    col_to_keep = [col for col in df if 'Unnamed' not in col]
    df = df[col_to_keep]

    if ffill_cols:
        for col in ffill_cols:
            df[col] = df[col].replace('', pd.NA).ffill()

    if date_col:
        for col in date_col:
            df[col] = datetime.now().strftime("%Y-%m-%d")

    return df



def generate_deterministic_row_ids(df):
    """
    Generate deterministic IDs based on transaction content.
    Handles duplicate transactions (same date, description, amount, source) 
    by adding incremental suffixes.
    
    Args:
        df: DataFrame with columns: Date, Description, Amount, Source, File
        
    Returns:
        Series of unique 8-character RowIDs
    """
    # Create a base hash for each row
    def create_hash_key(row):
        """Create a stable string representation of the transaction"""
        date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        desc = str(row['Description']).strip().lower()
        amount = f"{float(row['Amount']):.2f}"
        source = str(row['Source']).strip()
        file = str(row['File']).strip()
        return f"{date_str}|{desc}|{amount}|{source}|{file}"
    
    # Track duplicate counts for each unique transaction
    hash_counter = defaultdict(int)
    row_ids = []
    
    for idx, row in df.iterrows():
        base_key = create_hash_key(row)
        
        # Get the count for this transaction (0 for first occurrence)
        occurrence = hash_counter[base_key]
        hash_counter[base_key] += 1
        
        # Add suffix for duplicates
        if occurrence > 0:
            hash_input = f"{base_key}|dup_{occurrence}"
        else:
            hash_input = base_key
        
        # Generate 8-character hash
        row_id = hashlib.md5(hash_input.encode()).hexdigest()[:20]
        row_ids.append(row_id)
    
    return pd.Series(row_ids, index=df.index)
