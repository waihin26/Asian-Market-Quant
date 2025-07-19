"""
Data Loader for Asian Market Quant Project
-----------------------------------------
This module provides functions to load and preprocess the Excel data.
"""

import pandas as pd
import os
from pathlib import Path
from src.asset_class_mapping import (
    create_ticker_to_asset_class_map,
    categorize_columns,
    ASSET_MAPPING,
    RISK_BUDGET
)

def load_data(file_path, skip_rows=7, header_row=3):
    """
    Load data from Excel file.
    
    Parameters:
    - file_path: Path to the Excel file
    - skip_rows: Number of rows to skip for the data (default: 7)
    - header_row: Row number (0-indexed) containing column headers (default: 3 for row 4)
    
    Returns:
    - DataFrame with the price data
    """
    try:
        # First extract the proper column headers
        headers_df = pd.read_excel(file_path, skiprows=header_row, nrows=1)
        column_headers = headers_df.values.flatten().tolist()
        
        # Clean up the headers - replace unnamed columns and NaN values
        for i in range(len(column_headers)):
            if pd.isna(column_headers[i]) or 'Unnamed' in str(column_headers[i]):
                if i == 0:
                    column_headers[i] = 'Date'
                else:
                    column_headers[i] = f'Column_{i+1}'
            elif '#N/A' in str(column_headers[i]):
                # Replace Bloomberg #N/A values with more descriptive names
                column_headers[i] = f'NA_Column_{i+1}'
        
        # Now load the actual data with proper column headers
        df = pd.read_excel(file_path, skiprows=skip_rows, header=None)
        
        # Assign the extracted headers to the dataframe
        if len(df.columns) == len(column_headers):
            df.columns = column_headers
        else:
            print(f"Warning: Column count mismatch. Headers: {len(column_headers)}, Data columns: {len(df.columns)}")
            # Try to match as many as possible
            min_cols = min(len(df.columns), len(column_headers))
            df.columns = column_headers[:min_cols] + [f'Column_{i+1}' for i in range(min_cols, len(df.columns))]
        
        # Set the first column (assuming it contains dates) as the index
        if 'Date' in df.columns:
            df.set_index('Date', inplace=True)
        else:
            # If the date column has a different name or is already an index
            first_col = df.columns[0]
            if pd.api.types.is_datetime64_any_dtype(df[first_col]) or 'date' in str(first_col).lower():
                df.set_index(first_col, inplace=True)
        
        # Convert index to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            try:
                df.index = pd.to_datetime(df.index)
                print("Converted index to datetime format")
            except Exception as e:
                print(f"Could not convert index to datetime: {e}")
                
        print(f"Data loaded successfully: {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def preprocess_data(df):
    """
    Preprocess the loaded data.
    
    Parameters:
    - df: DataFrame with price data
    
    Returns:
    - Preprocessed DataFrame
    """
    if df is None:
        return None
    
    # Copy to avoid modifying the original
    df_processed = df.copy()
    
    # Convert index to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df_processed.index):
        df_processed.index = pd.to_datetime(df_processed.index)
    
    # Resample to business days and forward-fill missing values
    df_processed = df_processed.asfreq('B').ffill()
    
    # Check for any remaining missing values
    missing_values = df_processed.isna().sum().sum()
    if missing_values > 0:
        print(f"Warning: {missing_values} missing values remain after preprocessing")
    
    print(f"Data preprocessed successfully")
    return df_processed

def split_by_asset_class(df):
    """
    Split a DataFrame into multiple DataFrames based on asset classes.
    
    Parameters:
    - df: DataFrame with price data
    
    Returns:
    - Dictionary mapping asset classes to DataFrames
    """
    ticker_map = create_ticker_to_asset_class_map()
    asset_class_columns = categorize_columns(df, ticker_map)
    
    result = {}
    for asset_class, columns in asset_class_columns.items():
        result[asset_class] = df[columns].copy()
        print(f"Created DataFrame for {asset_class} with {len(columns)} columns")
    
    return result

def save_data(df, file_path, sheet_name='Processed Data'):
    """
    Save data to Excel or pickle file.
    
    Parameters:
    - df: DataFrame to save
    - file_path: Path to save the file
    - sheet_name: Sheet name for Excel files
    
    Returns:
    - True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save based on file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.xlsx' or ext == '.xls':
            df.to_excel(file_path, sheet_name=sheet_name)
        elif ext == '.pkl':
            df.to_pickle(file_path)
        elif ext == '.csv':
            df.to_csv(file_path)
        else:
            print(f"Unsupported file extension: {ext}")
            return False
        
        print(f"Data saved successfully to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def create_data_dictionary(df, output_path):
    """
    Create a data dictionary with information about each column.
    
    Parameters:
    - df: DataFrame with price data
    - output_path: Path to save the data dictionary
    
    Returns:
    - True if successful, False otherwise
    """
    ticker_map = create_ticker_to_asset_class_map()
    
    try:
        data_dict = []
        for column in df.columns:
            asset_info = ticker_map.get(column, {})
            
            # Get column type safely
            try:
                dtype_str = str(df[column].dtype)
            except:
                dtype_str = "Unknown"
                
            # Count non-null values safely
            try:
                non_null_count = df[column].count()
            except:
                non_null_count = 0
                
            # Calculate missing values percentage safely
            try:
                missing_pct = round(100 * df[column].isna().sum() / len(df), 2)
            except:
                missing_pct = 0
            
            data_dict.append({
                'Column Name': str(column),
                'Asset Class': asset_info.get('asset_class', 'Unknown'),
                'Description': asset_info.get('description', ''),
                'Currency': asset_info.get('currency', 'Unknown'),
                'Risk Bucket': asset_info.get('risk_bucket', 'Unknown'),
                'Data Type': dtype_str,
                'Non-Null Count': non_null_count,
                'Missing Values (%)': missing_pct
            })
        
        # Convert to DataFrame and save
        data_dict_df = pd.DataFrame(data_dict)
        
        # Save to Excel
        data_dict_df.to_excel(output_path, index=False, sheet_name='Data Dictionary')
        
        print(f"Data dictionary created and saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error creating data dictionary: {e}")
        return False

def main():
    """Example usage of the data loading module."""
    print("Data Loader for Asian Market Quant Project")
    print("=========================================")
    
    # Example paths
    excel_file = input("Enter path to Excel file: ")
    if not os.path.exists(excel_file):
        print(f"File not found: {excel_file}")
        return
    
    # Load data
    df = load_data(excel_file)
    if df is None:
        return
    
    # Preprocess data
    df_processed = preprocess_data(df)
    if df_processed is None:
        return
    
    # Split by asset class
    asset_dfs = split_by_asset_class(df_processed)
    
    # Create data directory structure
    base_dir = Path('data')
    raw_dir = base_dir / 'raw'
    processed_dir = base_dir / 'processed'
    
    for directory in [base_dir, raw_dir, processed_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Save original data
    excel_filename = os.path.basename(excel_file)
    save_data(df, raw_dir / excel_filename)
    
    # Save processed data
    save_data(df_processed, processed_dir / 'all_assets.pkl')
    save_data(df_processed, processed_dir / 'all_assets.xlsx')
    
    # Save individual asset class data
    for asset_class, asset_df in asset_dfs.items():
        save_data(asset_df, processed_dir / f"{asset_class}.pkl")
    
    # Create data dictionary
    create_data_dictionary(df_processed, processed_dir / 'data_dictionary.xlsx')
    
    print("\nData processing complete. Files saved to data/raw and data/processed directories.")

if __name__ == "__main__":
    main()
