"""
Asset Class Mapping for Asian Market Quant Project
-------------------------------------------------
This module provides functions to categorise tickers into asset classes,
generate a LaTeX-formatted table, and set up initial risk budgeting structures.
"""

import pandas as pd
import os
from pathlib import Path

# Define asset classes and their mappings
ASSET_MAPPING = {
    'emerging_asia_equity': {
        'tickers': [
            'MXAP Index', 'MXAPJ Index', 'MXAS Index', 'MXASJ Index',
            'PCOMP Index', 'JCI Index', 'FBMKLCI Index', 'SET Index',
            'STI Index', 'NU710465 Index', 'EPHE US Index', 'FMETF PM Equity'
        ],
        'description': 'Emerging-Asia equity indices & ETF',
        'currency': 'Mostly USD',
        'comment': 'Regional beta + macro sensitivity',
        'risk_bucket': 'equities'  # For risk budgeting
    },
    'commodities': {
        'tickers': ['GOLDS Index', 'CO1 Comdty', 'S 1 Comdty'],
        'description': 'Commodities (Gold spot, Brent front-month, generic Softs)',
        'currency': 'USD',
        'comment': 'Adds inflation hedge, carry via roll',
        'risk_bucket': 'commodities'  # For risk budgeting
    },
    'developed_equity': {
        'tickers': ['SPX Index', 'NKY Index'],
        'description': 'Developed-market equity benchmarks',
        'currency': 'USD / JPY',
        'comment': 'Good stress-test proxies',
        'risk_bucket': 'equities'  # For risk budgeting
    },
    'fx_crosses': {
        'tickers': ['USDPHP Index', 'USDMYR Index', 'USDIDR Index', 'USDSGD Index', 'USDJPY Curncy'],
        'description': 'EM & DM FX crosses vs USD',
        'currency': 'USD notional',
        'comment': 'Carry + momentum rich',
        'risk_bucket': 'fx'  # For risk budgeting
    },
    'sovereign_yields': {
        'tickers': ['USGG5YR Index', 'GTPHP5yr Corp', 'GTUSDPH5Y Corp'],
        'description': 'Sovereign & quasi-sovereign 5-yr yields',
        'currency': 'USD & PHP',
        'comment': 'Duration + EM credit risk',
        'risk_bucket': 'rates'  # For risk budgeting
    }
}

# Defining risk budgeting allocations
RISK_BUDGET = {
    'equities': 0.60,    # 60% allocation to equities
    'rates': 0.20,       # 20% allocation to rates
    'fx': 0.10,          # 10% allocation to FX
    'commodities': 0.10  # 10% allocation to commodities
}

def create_ticker_to_asset_class_map():
    """Creates a dictionary mapping each ticker to its asset class."""
    ticker_map = {}
    for asset_class, details in ASSET_MAPPING.items():
        for ticker in details['tickers']:
            ticker_map[ticker] = {
                'asset_class': asset_class,
                'description': details['description'],
                'currency': details['currency'],
                'comment': details['comment'],
                'risk_bucket': details['risk_bucket']
            }
    return ticker_map

def get_asset_class_for_ticker(ticker, ticker_map=None):
    """Returns the asset class for a given ticker."""
    if ticker_map is None:
        ticker_map = create_ticker_to_asset_class_map()
    
    return ticker_map.get(ticker, {}).get('asset_class', 'unknown')

def generate_latex_table():
    """Generates a LaTeX-formatted table of asset classes."""
    latex = "\\begin{table}[h]\n"
    latex += "\\centering\n"
    latex += "\\caption{Asset Class Mapping for Asian Markets}\n"
    latex += "\\begin{tabular}{|l|l|l|l|}\n"
    latex += "\\hline\n"
    latex += "\\textbf{Ticker Range} & \\textbf{Asset Class} & \\textbf{Currency} & \\textbf{Comment} \\\\ \\hline\n"
    
    for asset_class, details in ASSET_MAPPING.items():
        ticker_range = f"{details['tickers'][0].split()[0]} ... {details['tickers'][-1].split()[0]}"
        latex += f"{ticker_range} & {details['description']} & {details['currency']} & {details['comment']} \\\\ \\hline\n"
    
    latex += "\\end{tabular}\n"
    latex += "\\end{table}\n"
    return latex

def load_data(file_path, skip_rows=7):
    """
    Load data from Excel file.
    
    Parameters:
    - file_path: Path to the Excel file
    - skip_rows: Number of rows to skip (default: 7, based on our excel file)
    
    Returns:
    - DataFrame with the price data
    """
    try:
        # Read the Excel file, skipping rows as needed
        df = pd.read_excel(file_path, skiprows=skip_rows)
        
        # Set the first column (assuming it contains dates) as the index
        if 'Date' in df.columns:
            df.set_index('Date', inplace=True)
        else:
            # If the date column has a different name or is already an index
            first_col = df.columns[0]
            if pd.api.types.is_datetime64_any_dtype(df[first_col]) or 'date' in first_col.lower():
                df.set_index(first_col, inplace=True)
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def categorize_columns(df, ticker_map=None):
    """
    Categorize the columns in a DataFrame according to asset classes.
    
    Parameters:
    - df: DataFrame with price data
    - ticker_map: Map of tickers to asset classes (will create if None)
    
    Returns:
    - Dictionary mapping asset classes to lists of column names
    """
    if ticker_map is None:
        ticker_map = create_ticker_to_asset_class_map()
    
    asset_class_columns = {}
    unknown_columns = []
    
    for col in df.columns:
        asset_class = get_asset_class_for_ticker(col, ticker_map)
        if asset_class != 'unknown':
            if asset_class not in asset_class_columns:
                asset_class_columns[asset_class] = []
            asset_class_columns[asset_class].append(col)
        else:
            unknown_columns.append(col)
    
    if unknown_columns:
        print(f"Warning: Could not categorize these columns: {unknown_columns}")
    
    return asset_class_columns

def generate_markdown_table():
    """Generates a markdown-formatted table of asset classes for the README."""
    markdown = "| Ticker Range | Asset Class | Currency | Comment |\n"
    markdown += "|-------------|------------|----------|--------|\n"
    
    for asset_class, details in ASSET_MAPPING.items():
        ticker_range = f"{details['tickers'][0].split()[0]} ... {details['tickers'][-1].split()[0]}"
        markdown += f"| {ticker_range} | {details['description']} | {details['currency']} | {details['comment']} |\n"
    
    return markdown

def print_risk_budget():
    """Prints the risk budget allocation."""
    print("\nRisk Budget Allocation:")
    print("-----------------------")
    for bucket, allocation in RISK_BUDGET.items():
        print(f"{bucket.capitalize()}: {allocation*100:.1f}%")

def main():
    """Main function to demonstrate usage."""
    print("Asset Class Mapping for Asian Market Quant Project")
    print("=================================================")
    
    # Create and display the ticker mapping
    ticker_map = create_ticker_to_asset_class_map()
    
    # Count tickers by asset class
    asset_class_counts = {}
    for ticker, details in ticker_map.items():
        asset_class = details['asset_class']
        if asset_class not in asset_class_counts:
            asset_class_counts[asset_class] = 0
        asset_class_counts[asset_class] += 1
    
    print("\nTicker Distribution:")
    print("-------------------")
    for asset_class, count in asset_class_counts.items():
        print(f"{asset_class}: {count} tickers")
    
    # Print risk budget
    print_risk_budget()
    
    # Generate LaTeX table (sample output)
    print("\nLaTeX Table Sample:")
    print("------------------")
    latex_table = generate_latex_table()
    print(latex_table[:300] + "...\n")
    
    print("To use this module, import it and use the functions to load and categorize your data.")
    print("Example:")
    print("    from asset_class_mapping import load_data, categorize_columns")
    print("    df = load_data('path/to/your/excel_file.xlsx')")
    print("    asset_classes = categorize_columns(df)")

if __name__ == "__main__":
    main()
