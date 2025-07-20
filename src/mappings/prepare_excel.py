"""
This script copies the raw Excel into data/processed/, reads the row for tickers and matches them to ASSET_MAPPING buckets.
It then prints a categorized summary of found vs. missing tickers with validation checks.

Usage:
    python prepare_excel.py path/to/excel_file.xlsx
"""

import sys
import pandas as pd
import os
import shutil
from pathlib import Path

def prepare_excel_file(excel_path, output_dir='data/processed'):
    """
    Prepares the Excel file for further processing:
    1. Creates a copy of the original file
    2. Checks the structure and ensures headers are correctly identified
    
    Args:
        excel_path (str): Path to the original Excel file
        output_dir (str): Directory to save the processed file
    
    Returns:
        str: Path to the prepared Excel file
    """
    print(f"Preparing Excel file: {excel_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the filename
    filename = os.path.basename(excel_path)
    output_path = os.path.join(output_dir, filename)
    
    # Check if source file exists
    if not os.path.exists(excel_path):
        print(f"Error: Source file not found - {excel_path}")
        return None
    
    # Copy the file to the output directory
    shutil.copy(excel_path, output_path)
    print(f"File copied to {output_path}")
    
    # Read the Excel file to check structure
    try:
        # Load the column headers from row 4 (index 3)
        headers_df = pd.read_excel(excel_path, skiprows=3, nrows=1)
        column_names = headers_df.columns.tolist()
        
        print("\nDetected column headers:")
        for i, col in enumerate(column_names):
            print(f"  {i+1}. {col}")
        
        print("\nChecking for ticker formats...")
        
        # Import the predefined asset mapping from our module
        try:
            # First try to import directly
            sys.path.append('.')
            from src.asset_class_mapping import ASSET_MAPPING
            
            # Initialize categorized dictionary based on our asset mapping
            categorized = {asset_class: [] for asset_class in ASSET_MAPPING.keys()}
            uncategorized = []
            
            # Create a lookup dictionary for faster categorization
            ticker_to_class = {}
            for asset_class, details in ASSET_MAPPING.items():
                for ticker in details['tickers']:
                    ticker_to_class[ticker] = asset_class
            
            # Categorize columns based on exact ticker matches
            for col in column_names:
                if col in ticker_to_class:
                    asset_class = ticker_to_class[col]
                    categorized[asset_class].append(col)
                else:
                    uncategorized.append(col)
                    
        except ImportError:
            # Fallback to simple categorization if import fails
            print("Warning: Could not import asset class mapping. Using simple categorization.")
            ticker_formats = {
                "emerging_asia_equity": ['MXAP', 'MXAPJ', 'MXAS', 'MXASJ', 'PCOMP', 'JCI', 'FBMKLCI', 'SET', 'STI', 'NU710465', 'EPHE'],
                "commodities": ['GOLDS', 'CO1', 'S 1', 'FMETF PM'],
                "developed_equity": ['SPX', 'NKY'],
                "fx_crosses": ['USDPHP', 'USDMYR', 'USDIDR', 'USDSGD', 'USDJPY'],
                "sovereign_yields": ['USGG5YR', 'GTPHP5yr', 'GTUSDPH5Y']
            }
            
            # Initialize categorized dictionary
            categorized = {category: [] for category in ticker_formats}
            uncategorized = []
            
            # Categorize columns based on ticker prefixes
            for col in column_names:
                categorized_flag = False
                for category, prefixes in ticker_formats.items():
                    if any(prefix in col for prefix in prefixes):
                        categorized[category].append(col)
                        categorized_flag = True
                        break
                
                if not categorized_flag:
                    uncategorized.append(col)
        
        print("\nAutomatically categorized tickers:")
        for category, tickers in categorized.items():
            if tickers:
                # Format the category name more nicely
                category_display = category.replace('_', ' ').title()
                print(f"\n{category_display}:")
                for ticker in tickers:
                    print(f"  - {ticker}")
        
        if uncategorized:
            print("\nUncategorized tickers:")
            for ticker in uncategorized:
                print(f"  - {ticker}")
        
        # Load some sample data to check format
        print("\nLoading sample data rows...")
        sample_data = pd.read_excel(excel_path, skiprows=7, nrows=5)
        print(sample_data.head())
        
        # Validate the categorization against expected tickers
        print("\nValidation Summary:")
        total_tickers = sum(len(tickers) for tickers in categorized.values())
        print(f"Total categorized tickers: {total_tickers}")
        print(f"Uncategorized tickers: {len(uncategorized)}")
        
        try:
            # Check against expected counts from ASSET_MAPPING
            from src.asset_class_mapping import ASSET_MAPPING
            expected_counts = {asset_class: len(details['tickers']) for asset_class, details in ASSET_MAPPING.items()}
            
            print("\nExpected vs. Actual Ticker Counts:")
            for asset_class in ASSET_MAPPING.keys():
                expected = expected_counts.get(asset_class, 0)
                actual = len(categorized.get(asset_class, []))
                
                status = "✓" if expected == actual else "❌"
                print(f"{asset_class}: Expected {expected}, Found {actual} {status}")
                
                # If mismatch, show the differences
                if expected != actual and asset_class in categorized:
                    expected_tickers = set(ASSET_MAPPING[asset_class]['tickers'])
                    actual_tickers = set(categorized[asset_class])
                    
                    missing = expected_tickers - actual_tickers
                    extra = actual_tickers - expected_tickers
                    
                    if missing:
                        print(f"  Missing: {', '.join(missing)}")
                    if extra:
                        print(f"  Extra: {', '.join(extra)}")
        except ImportError:
            print("Could not validate against ASSET_MAPPING (module not found).")
        
        return output_path
        
    except Exception as e:
        print(f"Error checking Excel structure: {e}")
        return None

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python prepare_excel.py path/to/excel_file.xlsx")
        return
    
    excel_path = sys.argv[1]
    prepared_path = prepare_excel_file(excel_path)
    
    if prepared_path:
        print(f"\nExcel file prepared and saved to: {prepared_path}")
        print("\nNext steps:")
        print("Run `python main.py {prepared_path}` to perform asset class mapping")
    else:
        print("\nFailed to prepare Excel file.")

if __name__ == "__main__":
    main()
