from sqlalchemy import text
from database import init_db, engine
import pandas as pd

def load_all_spending_from_db() -> pd.DataFrame:
    """Load all spending records from the database into a DataFrame."""
    return pd.read_sql("SELECT * FROM AllSpending", engine)

def insert_new_records(df: pd.DataFrame, engine, table_name: str = 'AllSpending'):
    """
    Insert only records that don't already exist in the database.
    
    Args:
        df: DataFrame with RowID column
        engine: SQLAlchemy engine
        table_name: Target table name
        
    Returns:
        Number of new records inserted
    """
    # Get existing RowIDs from database
    existing_ids = pd.read_sql(
        f"SELECT RowID FROM {table_name}", 
        engine
    )['RowID'].tolist()
    
    # Filter to only new records
    new_records = df[~df['RowID'].isin(existing_ids)]
    
    if len(new_records) == 0:
        print("No new records to insert")
        return 0
    
    # Insert new records
    new_records.to_sql(table_name, engine, if_exists='append', index=False)
    
    print(f"Inserted {len(new_records)} new records (skipped {len(df) - len(new_records)} existing)")
    return len(new_records)

