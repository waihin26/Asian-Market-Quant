"""
Main script for the Asian Market Quant project - Asset Class Mapping step.

This script:
1. Loads the Excel data
2. Maps tickers to asset classes 
3. Generates LaTeX tables for reporting

Usage:
    python main.py [excel_file_path]
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Import project modules
from src.asset_class_mapping import (
    create_ticker_to_asset_class_map, 
    categorize_columns,
    ASSET_MAPPING, 
    RISK_BUDGET
)
from src.data_loader import (
    load_data,
    preprocess_data,
    split_by_asset_class,
    save_data,
    create_data_dictionary
)
from src.latex_generator import (
    generate_asset_class_table,
    generate_risk_budget_table,
    generate_full_latex_document
)

def setup_directories():
    """Create the project directory structure."""
    base_dir = Path('.')
    dirs = [
        base_dir / 'data',
        base_dir / 'data' / 'raw',
        base_dir / 'data' / 'processed',
        base_dir / 'output',
        base_dir / 'output' / 'latex',
        base_dir / 'output' / 'tables'
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    return dirs

def process_excel_file(excel_path):
    """Process the Excel file and generate all deliverables."""
    print(f"\nProcessing Excel file: {excel_path}")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(excel_path):
        print(f"Error: File not found - {excel_path}")
        return False
    
    # In your Excel: Row 1-3 are headers, Row 4 has ticker names, Row 5-6 has "Last Price"/"PX_Last", Row 8+ has data
    print("\n1. Loading column headers from Excel (ticker names)...")
    
    print("\nReading ticker names directly from Excel file...")
    try:
        ticker_row   = pd.read_excel(excel_path, skiprows=3, nrows=1)
        ticker_names = ticker_row.columns.tolist()
        print("Using ticker names from Excel row 4 column headers")

        if pd.isna(ticker_names[0]) or 'Unnamed' in str(ticker_names[0]) or ticker_names[0] == '':
            ticker_names[0] = 'Date'
            
        print(f"Found ticker names in Excel file:")
        for i, name in enumerate(ticker_names):
            print(f"  {i+1}. {name}")
        
        # Get expected tickers from asset mapping
        print("\nGetting expected tickers from asset_class_mapping...")
        all_expected_tickers = []
        for details in ASSET_MAPPING.values():
            all_expected_tickers.extend(details['tickers'])
        
        # Now load the actual data
        print("\nLoading data starting from row 8...")
        df = pd.read_excel(excel_path, skiprows=7, header=None)
        
        # Decide which column headers to use
        if ticker_names and ticker_names[0] == 'Date' and 'Last Price' not in ticker_names:
            print("Using ticker names from Excel file")
            columns_to_use = ticker_names
        else:
            print("Using expected tickers from asset_class_mapping")
            # First column is date
            columns_to_use = ['Date'] 
            # Add expected tickers as column headers
            for i in range(1, len(df.columns)):
                if i <= len(all_expected_tickers):
                    columns_to_use.append(all_expected_tickers[i-1])
                else:
                    columns_to_use.append(f'Column_{i}')
        
        # Ensure column count matches
        if len(df.columns) != len(columns_to_use):
            print(f"Warning: Column count mismatch. Headers: {len(columns_to_use)}, Data columns: {len(df.columns)}")
            if len(df.columns) > len(columns_to_use):
                # Add extra column names
                for i in range(len(columns_to_use), len(df.columns)):
                    columns_to_use.append(f'Column_{i+1}')
            else:
                # Truncate column names
                columns_to_use = columns_to_use[:len(df.columns)]
        
        # Assign headers to dataframe
        df.columns = columns_to_use
        
        # Set the date column as index
        if 'Date' in df.columns:
            df.set_index('Date', inplace=True)
        else:
            df.set_index(df.columns[0], inplace=True)
        
        print(f"Data loaded successfully: {df.shape[0]} rows and {df.shape[1]} columns")
    except Exception as e:
        print(f"Error loading data: {e}")
        df = None
    
    if df is None:
        print("Error: Could not load data. Exiting.")
        return False
    
    # Display the column names to check if they match what we expect
    print("\nActual columns in DataFrame:")
    for i, col in enumerate(df.columns):
        print(f"  {i+1}. {col}")
    
    # Preprocess the data
    print("\n2. Preprocessing data...")
    df_processed = preprocess_data(df)
    
    # Split by asset class
    print("\n3. Categorizing assets...")
    asset_dfs = split_by_asset_class(df_processed)
    
    # Summary of categorization
    print("\nAsset Class Summary:")
    print("-" * 50)
    for asset_class, asset_df in asset_dfs.items():
        print(f"{asset_class.capitalize()}: {asset_df.shape[1]} tickers")
        for col in asset_df.columns:
            print(f"  - {col}")
    
    # Save processed data
    print("\n4. Saving processed data...")
    save_data(df, 'data/raw/original_data.xlsx')
    save_data(df_processed, 'data/processed/all_assets.pkl')
    save_data(df_processed, 'data/processed/all_assets.xlsx')
    
    # Save individual asset class data
    for asset_class, asset_df in asset_dfs.items():
        save_data(asset_df, f'data/processed/{asset_class}.pkl')
     
    # Generate LaTeX files
    print("\n5. Generating LaTeX tables...")
    os.makedirs('output/latex', exist_ok=True)
    
    with open('output/latex/asset_class_table.tex', 'w') as f:
        f.write(generate_asset_class_table())
    
    with open('output/latex/risk_budget_table.tex', 'w') as f:
        f.write(generate_risk_budget_table())
    
    with open('output/latex/asset_class_mapping.tex', 'w') as f:
        f.write(generate_full_latex_document())
    
    print("\nAll processing complete!")
    print("=" * 50)
    print("\nDeliverables:")
    print("1. Asset class mapping table (output/latex/asset_class_table.tex)")
    print("2. Risk budget table (output/latex/risk_budget_table.tex)")
    print("3. Full LaTeX document (output/latex/asset_class_mapping.tex)")
    print("4. Processed data (data/processed/all_assets.xlsx)")
    
    print("\nNext steps:")
    print("1. Compile the LaTeX document to generate a PDF report")
    print("2. Continue to the Data Engineering Pipeline step")
    print("3. Begin exploratory data analysis")
    
    return True

def fix_and_process_excel(excel_path):
    """
    Try to fix a problematic Excel file and then process it.
    
    Args:
        excel_path: Path to the Excel file to fix and process
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create a fixed version of the Excel file
    try:
        import pandas as pd
        from src.asset_class_mapping import ASSET_MAPPING
        
        print("\nTrying to fix the Excel file structure...")
        
        # Define expected tickers based on asset_class_mapping
        expected_tickers = []
        for details in ASSET_MAPPING.values():
            expected_tickers.extend(details['tickers'])
        
        # Get the base filename
        basename = os.path.basename(excel_path)
        output_path = os.path.join('data/processed', f"fixed_{basename}")
        
        # Load the data
        data = pd.read_excel(excel_path, skiprows=7, header=None)
        
        # Create column headers - first column is Date
        headers = ['Date']
        
        # Add remaining headers from expected tickers
        for i in range(1, len(data.columns)):
            if i-1 < len(expected_tickers):
                headers.append(expected_tickers[i-1])
            else:
                headers.append(f'Column_{i}')
        
        # Set column names
        data.columns = headers
        
        # Save fixed file
        data.to_excel(output_path, index=False)
        
        print(f"Fixed Excel file created at: {output_path}")
        print(f"\nProcessing fixed Excel file: {output_path}")
        
        return process_excel_file(output_path)
    except Exception as e:
        print(f"\nError fixing Excel file: {e}")
        return False

def main():
    """Main entry point."""
    print("Asian Market Quant Project - Asset Class Mapping")
    print("=" * 50)
    
    # Setup project structure
    setup_directories()
    
    # Get Excel file path from command line or prompt
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        excel_path = input("Enter path to your Excel file: ")
    
    # Check if the file exists
    if not os.path.exists(excel_path):
        print(f"Error: File not found - {excel_path}")
        return
    
    # Check if this is the first run or a retry with a fixed file
    is_fixed_file = "fixed_" in os.path.basename(excel_path)
    
    # Process the Excel file
    if is_fixed_file:
        # Already a fixed file, just process it
        success = process_excel_file(excel_path)
    else:
        # Try processing directly first
        print("Attempting standard processing...")
        success = process_excel_file(excel_path)
        
        # If standard processing failed, try fixing the file
        if not success:
            print("\nStandard processing failed. Attempting to fix and reprocess...")
            success = fix_and_process_excel(excel_path)
    
    if success:
        print("\nAsset Class Mapping step completed successfully!")
    else:
        print("\nAsset Class Mapping step failed. Please check the error messages above.")
        print("\nTry manually fixing the Excel file structure:")
        print("1. Ensure row 3 contains actual ticker names (MXAP Index, SPX Index, etc.)")
        print("2. Ensure data starts from row 8")
        print("3. Save the fixed file and run this script again")

if __name__ == "__main__":
    main()
