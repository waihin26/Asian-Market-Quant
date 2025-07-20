# .gitignore

```
# Python __pycache__/ *.pyc *.pyo *.pyd *.env .env .venv/ venv/ *.egg-info/ dist/ build/ # Jupyter .ipynb_checkpoints/ # OS files .DS_Store Thumbs.db # VS Code .vscode/
```

# data/processed/all_assets.pkl

This is a binary file of the type: Binary

# data/processed/all_assets.xlsx

This is a binary file of the type: Excel Spreadsheet

# data/processed/commodities.pkl

This is a binary file of the type: Binary

# data/processed/data_dictionary.xlsx

This is a binary file of the type: Excel Spreadsheet

# data/processed/developed_equity.pkl

This is a binary file of the type: Binary

# data/processed/emerging_asia_equity.pkl

This is a binary file of the type: Binary

# data/processed/fx_crosses.pkl

This is a binary file of the type: Binary

# data/processed/MSCI_Comps.xlsx

This is a binary file of the type: Excel Spreadsheet

# data/processed/sovereign_yields.pkl

This is a binary file of the type: Binary

# data/raw/MSCI_Comps.xlsx

This is a binary file of the type: Excel Spreadsheet

# data/raw/original_data.xlsx

This is a binary file of the type: Excel Spreadsheet

# main.py

```py
"""
Main script for the Asian Market Quant project - Asset Class Mapping step.

This script:
1. Loads the Excel data
2. Maps tickers to asset classes 
3. Generates LaTeX tables for reporting
4. Creates a data dictionary

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
    
    # Create data dictionary
    create_data_dictionary(df_processed, 'data/processed/data_dictionary.xlsx')
    
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
    print("5. Data dictionary (data/processed/data_dictionary.xlsx)")
    
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

```

# output/latex/asset_class_mapping.tex

```tex
\documentclass{article} \usepackage[margin=1in]{geometry} \usepackage{tabularx} \usepackage{booktabs} \usepackage{color} \usepackage{graphicx} \title{Asset Class Mapping for Asian Market Quant Project} \author{Wong Wai Hin} \date{\today} \begin{document} \maketitle \section{Asset Class Mapping} This document outlines the asset class categorization for our cross-asset Asian markets project. We have categorized the tickers into five main asset classes for systematic analysis and risk budgeting. \begin{table}[h!] \centering \caption{Asset Class Mapping for Asian Markets} \label{tab:asset_class_mapping} \begin{tabularx}{\textwidth}{|l|X|l|X|} \hline \textbf{Ticker Range} & \textbf{Asset Class} & \textbf{Currency} & \textbf{Comment} \\ \hline MXAP \ldots FMETF & Emerging-Asia equity indices & Mostly USD & Regional beta + macro sensitivity \\ \hline GOLDS \ldots S & Commodities (Gold spot, Brent front-month, generic Softs, Philippines gold ETF) & USD & Adds inflation hedge, carry via roll \\ \hline SPX \ldots NKY & Developed-market equity benchmarks & USD / JPY & Good stress-test proxies \\ \hline USDPHP \ldots USDJPY & FX & USD notional & Carry + momentum rich \\ \hline USGG5YR \ldots GTUSDPH5Y & Sovereign & USD & Duration + EM credit risk \\ \hline \end{tabularx} \end{table} \section{Risk Budgeting Framework} Based on our asset class mapping, we propose the following risk budget allocation for portfolio construction. This allocation will be used in the hierarchical risk parity (HRP) overlay. \begin{table}[h!] \centering \caption{Risk Budget Allocation} \label{tab:risk_budget} \begin{tabular}{|l|c|} \hline \textbf{Asset Class} & \textbf{Allocation (\%)} \\ \hline Equities & 60.0\% \\ \hline Rates & 20.0\% \\ \hline Fx & 10.0\% \\ \hline Commodities & 10.0\% \\ \hline \end{tabular} \end{table} \section{Asset Class Descriptions} \subsection{Emerging-Asia Equity} This category includes the major Asian equity indices (MXAP, MXAS) and country-specific indices (PCOMP for Philippines, JCI for Indonesia, etc.). These provide exposure to regional beta with varying degrees of macro sensitivity. \subsection{Commodities} Our commodity exposure includes gold spot (GOLDS), Brent crude front-month (CO1), generic Softs (S 1), and a Philippines gold ETF (FMETF). This basket provides inflation hedging properties and potential carry from rolling futures contracts. \subsection{Developed-Market Equity} We include S\&P 500 (SPX) and Nikkei 225 (NKY) as developed market benchmarks that serve as useful proxies for stress testing our portfolio and measuring correlation regimes. \subsection{FX Crosses} We track several USD crosses including USDPHP, USDMYR, USDIDR, USDSGD, and USDJPY. These provide exposure to carry and momentum factors that tend to work well in Asia. \subsection{Sovereign Yields} Our rates exposure includes 5-year sovereign yields: US Treasury (USGG5YR), Philippine government bonds (GTPHP5yr), and USD-denominated Philippine sovereign debt (GTUSDPH5Y). These provide duration exposure and EM credit risk. \section{Next Steps} With this asset class mapping complete, we will proceed to: \begin{enumerate} \item Implement data cleaning and currency normalization \item Perform exploratory analysis to identify correlations and regime changes \item Design signal prototypes for each asset class \item Apply hierarchical risk parity within our risk budget framework \end{enumerate} \end{document}
```

# output/pdfs/asset_class_mapping.pdf

This is a binary file of the type: PDF

# prepare_excel.py

```py
"""
Script to prepare the Excel data for the Asian Market Quant project.
This script helps organize the Excel file, placing it in the right format.

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
        
        # Now load some sample data to check format
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
        print("1. Run `python main.py {prepared_path}` to perform asset class mapping")
        print("2. Or open the notebook: `jupyter notebook notebooks/01_asset_class_mapping.ipynb`")
    else:
        print("\nFailed to prepare Excel file.")

if __name__ == "__main__":
    main()

```

# QUICKSTART.md

```md
# Asian Market Quant Project - Quick Start Guide This guide provides step-by-step instructions to complete the first task of the project: **Scoping & Asset-Class Mapping**. ## Step 1: Setup Your Environment First, ensure you have all necessary dependencies installed: \`\`\`bash # Install required Python packages pip install pandas numpy matplotlib seaborn openpyxl xlrd jupyter \`\`\` Or simply use the requirements file: \`\`\`bash pip install -r requirements.txt \`\`\` ## Step 2: Prepare Your Excel File 1. Place your Excel file containing the market data in a known location 2. Run the preparation script to analyze the file structure: \`\`\`bash python prepare_excel.py path/to/your/excel_file.xlsx \`\`\` This will: - Copy your file to the `data/raw` directory - Analyze the column headers to identify ticker types - Display sample data to confirm the format ## Step 3: Process the Data and Create Asset Class Mapping Choose one of these two methods: ### Option 1: Using the Python Script \`\`\`bash python main.py data/raw/your_excel_file.xlsx \`\`\` This will: - Load your data from Excel - Categorize the tickers into asset classes - Generate LaTeX tables for reporting - Save processed data files for future steps ### Option 2: Using the Jupyter Notebook \`\`\`bash jupyter notebook notebooks/01_asset_class_mapping.ipynb \`\`\` This provides an interactive experience where you can: - Follow along with detailed explanations - Visualize the asset class distribution - Modify the risk budget allocation if needed - Generate reports with your customizations ## Step 4: Review the Results After running either option, you'll have: 1. **Processed Data Files** in `data/processed/` - `all_assets.xlsx` - The full dataset - `all_assets.pkl` - Pickled version for faster loading - Individual asset class files (e.g., `emerging_asia_equity.pkl`) - `data_dictionary.xlsx` - Documentation of all data fields 2. **LaTeX Reports** in `output/latex/` - `asset_class_mapping.tex` - Complete LaTeX document - `asset_class_table.tex` - Just the asset mapping table - `risk_budget_table.tex` - Just the risk budget table 3. **Tables** in `output/tables/` - CSV files containing the mapping data ## Step 5: Generate the Final Report If you have LaTeX installed, you can generate the PDF report: \`\`\`bash cd output/latex pdflatex asset_class_mapping.tex \`\`\` ## Next Steps After completing this first task, you're ready to move on to: 1. **Data Engineering Pipeline**: Currency normalization, corporate actions, etc. 2. **Exploratory Analysis**: Calculate summary statistics and correlations 3. **Signal Design**: Develop trading signals for each asset class For any issues or questions, refer to the full documentation in the README.md file.
```

# README.md

```md
# Asian Market Quant Research Project This repository provides a complete workflow for building a professional quant-research deck and dashboard for Asian cross-asset markets. The project is structured into six sequential workstreams, each with clear deliverables and recommended tools. ## Getting Started ### Prerequisites - Python 3.8+ - Jupyter Notebook - LaTeX (for generating reports) ### Installation 1. Clone the repository: \`\`\` git clone https://github.com/waihin26/Asian-Market-Quant.git cd Asian-Market-Quant \`\`\` 2. Install dependencies: \`\`\` pip install -r requirements.txt \`\`\` 3. Place your Excel data file in the `data/raw` directory. ### Usage You can work through the project steps in several ways: 1. **Using the Python scripts**: \`\`\` python main.py path/to/your/excel_file.xlsx \`\`\` 2. **Using the Jupyter notebooks**: \`\`\` cd notebooks jupyter notebook 01_asset_class_mapping.ipynb \`\`\` 3. **Generate LaTeX reports**: \`\`\` cd output/latex pdflatex asset_class_mapping.tex \`\`\` ## Project Structure \`\`\` Asian-Market-Quant/ ├── data/ │ ├── raw/ # Original data files │ └── processed/ # Cleaned and processed data ├── notebooks/ # Jupyter notebooks for each step ├── output/ │ ├── latex/ # LaTeX report files │ └── tables/ # CSV tables for analysis ├── src/ # Source code modules ├── requirements.txt # Python dependencies └── README.md # This file \`\`\` --- ## 1. Scoping & Asset-Class Mapping Map tickers to asset classes, currencies, and comments. Deliver a LaTeX-formatted table and define asset-class buckets for risk budgeting (e.g., 60% equities, 30% rates, 10% FX). | Ticker Range | Asset Class | Currency | Comment | | ---------------------------- | ----------------------------------------------------------- | ------------ | --------------------------------- | | MXAP … NU710465, EPHE | Emerging-Asia equity indices & ETF | Mostly USD | Regional beta + macro sensitivity | | GOLDS, CO1, S 1, FMETF | Commodities (Gold spot, Brent, Softs, Philippines gold ETF) | USD | Inflation hedge, carry via roll | | SPX, NKY | Developed-market equity benchmarks | USD / JPY | Stress-test proxies | | USDPHP … USDJPY | EM & DM FX crosses vs USD | USD notional | Carry + momentum rich | | USGG5YR, GTPHP5yr, GTUSDPH5Y | Sovereign & quasi-sovereign 5-yr yields | USD & PHP | Duration + EM credit risk | --- ## 2. Data Engineering Pipeline - **Ingest & tidy:** Load and clean spreadsheet data, resample to business days, forward-fill holidays. - **Currency normalization:** Convert all series to USD. - **Corporate actions & rolls:** Adjust for dividends, roll contracts before expiry. - **Store snapshots:** Organize raw and processed data in `data/`. **Deliverable:** Reproducible data module (`data_loader.py`) and a data dictionary. --- ## 3. Exploratory Analysis - Summary statistics: mean %, vol %, skew, kurtosis. - Correlations & regime analysis (e.g., 2008, COVID-19, 2022 inflation spike). - Rolling 12-month Sharpe heatmap. **Deliverable:** Jupyter notebook with charts and a “Market landscape” section for the deck. --- ## 4. Signal Design & Strategy Prototypes Design and backtest signals for each asset bucket: | Bucket | Classic Signals | PM-Wow Factor | | ----------- | --------------------------------- | --------------------------------- | | Equities | 12-1M momentum, 63-day breakout | Volatility-adjusted (risk parity) | | FX | Carry, 1-M momentum | “Dollar smile” overlay | | Rates | 2s5s10s butterfly, mean-reversion | Macro overlay (CPI surprises) | | Commodities | 6-/12-M momentum, roll yield | Seasonality dummies | - Write vectorized signal functions. - Backtest monthly with transaction costs and vol-targeting. - Report metrics: CAGR, Sharpe, Sortino, max drawdown, turnover, hit-rate, exposure heatmap. - Robustness: rolling windows, walk-forward OOS, parameter sweeps. **Deliverable:** `backtest_engine.py` and separate notebooks per prototype. --- ## 5. Portfolio Construction & Risk Budgeting - Top-down allocation (e.g., 60/30/10 split) via hierarchical risk parity (HRP). - Signal ensemble: combine best signals per bucket (equal risk or performance-weighted). - Stress tests: 2008, taper-tantrum, 2020 crash, 2022 inflation. - Optional: factor exposures (Barra or PCA). **Deliverable:** Notebook and PDF appendix “Risk & Allocation Methodology”. --- ## 6. Presentation & PM-Facing Assets | Asset | Purpose | Tips | | -------------------- | ----------------------- | ------------------------------------------- | | 10-slide Beamer deck | Executive summary | <15 min read-time, “Key Takeaways” up front | | Streamlit dashboard | Interactive exploration | Tabs: Performance, Positions, Risk | | Excel hand-off file | Quick inspection | Pivot table of monthly returns + tear-sheet | --- ## Recommended Tool Stack - **Python**: pandas, numpy, vectorbt/bt, PyPortfolioOpt, quantstats - **Git**: branch per prototype - **Environment**: conda env + `requirements.txt` - **Documentation**: MkDocs or simple `README.md` --- ## Suggested Timeline (Working Days) \`\`\` Day 1 Scope + data ingestion Day 2 Cleaning + basic EDA Day 3-5 Prototype 1–3 (momentum, carry, roll) Day 6 Robustness & risk budgeting Day 7 Build deck & dashboard Day 8 Buffer / iteration with PM feedback \`\`\` --- ## Final Checks Before Hand-off 1. Re-run all notebooks top-to-bottom on a fresh kernel. 2. Tag the Git release (e.g., v0.9-PMdemo). 3. Export deck to PDF and embed high-resolution figures. 4. Dry-run the Streamlit app locally and on Streamlit Community Cloud. --- ## Next Steps - Add alternative data (e.g., Alibaba traffic, PMI surprises). - Explore Bayesian ensemble for signal blending. - Model execution costs for production deployment. --- **Tackle one workstream at a time, commit early, and you’ll deliver a professional-grade project ready for PM review and further funding.**
```

# requirements.txt

```txt
# Core dependencies pandas==2.0.3 numpy==1.24.3 matplotlib==3.7.2 seaborn==0.12.2 # Data handling openpyxl==3.1.2 # For Excel file support xlrd==2.0.1 # For older Excel formats python-dateutil==2.8.2 # Jupyter environment (for notebooks) jupyter==1.0.0 notebook==6.5.4 ipywidgets==8.0.6 # Financial analysis vectorbt==0.25.4 pyportfolioopt==1.5.4 quantstats==0.0.62
```

# src/asset_class_mapping.py

```py
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
        'description': 'Commodities (Gold spot, Brent front-month, generic Softs, Philippines gold ETF)',
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
    # Example usage
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

```

# src/data_loader.py

```py
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

```

# src/latex_generator.py

```py
"""
LaTeX Table Generator for Asset Class Mapping
--------------------------------------------
This module creates LaTeX tables for the asset class mapping deliverable.
"""

from src.asset_class_mapping import ASSET_MAPPING, RISK_BUDGET

def generate_asset_class_table():
    """Generate a LaTeX table for asset class mapping."""
    latex = """
\\begin{table}[h!]
\\centering
\\caption{Asset Class Mapping for Asian Markets}
\\label{tab:asset_class_mapping}
\\begin{tabularx}{\\textwidth}{|l|X|l|X|}
\\hline
\\textbf{Ticker Range} & \\textbf{Asset Class} & \\textbf{Currency} & \\textbf{Comment} \\\\
\\hline
"""
    
    for asset_class, details in ASSET_MAPPING.items():
        # Format the ticker range to show first and last ticker
        first_ticker = details['tickers'][0].split()[0]
        last_ticker = details['tickers'][-1].split()[0]
        ticker_range = f"{first_ticker} \\ldots {last_ticker}"
        
        # Add a row to the table
        latex += f"{ticker_range} & {details['description']} & {details['currency']} & {details['comment']} \\\\\n\\hline\n"
    
    latex += """\\end{tabularx}
\\end{table}
"""
    
    return latex

def generate_risk_budget_table():
    """Generate a LaTeX table for risk budget allocation."""
    latex = """
\\begin{table}[h!]
\\centering
\\caption{Risk Budget Allocation}
\\label{tab:risk_budget}
\\begin{tabular}{|l|c|}
\\hline
\\textbf{Asset Class} & \\textbf{Allocation (\\%)} \\\\
\\hline
"""
    
    for bucket, allocation in RISK_BUDGET.items():
        # Format the allocation as a percentage
        alloc_pct = f"{allocation*100:.1f}\\%"
        
        # Add a row to the table
        latex += f"{bucket.capitalize()} & {alloc_pct} \\\\\n\\hline\n"
    
    latex += """\\end{tabular}
\\end{table}
"""
    
    return latex

def generate_full_latex_document():
    """Generate a complete LaTeX document with all tables."""
    latex = """
\\documentclass{article}
\\usepackage[margin=1in]{geometry}
\\usepackage{tabularx}
\\usepackage{booktabs}
\\usepackage{color}
\\usepackage{graphicx}

\\title{Asset Class Mapping for Asian Market Quant Project}
\\author{Asian Market Quant Team}
\\date{\\today}

\\begin{document}

\\maketitle

\\section{Asset Class Mapping}

This document outlines the asset class categorization for our cross-asset Asian markets project. 
We have categorized the tickers into five main asset classes for systematic analysis and risk budgeting.

"""
    
    latex += generate_asset_class_table()
    
    latex += """
\\section{Risk Budgeting Framework}

Based on our asset class mapping, we propose the following risk budget allocation for portfolio construction.
This allocation will be used in the hierarchical risk parity (HRP) overlay.

"""
    
    latex += generate_risk_budget_table()
    
    latex += """
\\section{Asset Class Descriptions}

\\subsection{Emerging-Asia Equity}
This category includes the major Asian equity indices (MXAP, MXAS) and country-specific indices 
(PCOMP for Philippines, JCI for Indonesia, etc.). These provide exposure to regional beta with 
varying degrees of macro sensitivity.

\\subsection{Commodities}
Our commodity exposure includes gold spot (GOLDS), Brent crude front-month (CO1), generic Softs (S 1), 
and a Philippines gold ETF (FMETF). This basket provides inflation hedging properties and potential
carry from rolling futures contracts.

\\subsection{Developed-Market Equity}
We include S\\&P 500 (SPX) and Nikkei 225 (NKY) as developed market benchmarks that serve as 
useful proxies for stress testing our portfolio and measuring correlation regimes.

\\subsection{FX Crosses}
We track several USD crosses including USDPHP, USDMYR, USDIDR, USDSGD, and USDJPY. 
These provide exposure to carry and momentum factors that tend to work well in Asia.

\\subsection{Sovereign Yields}
Our rates exposure includes 5-year sovereign yields: US Treasury (USGG5YR), Philippine government bonds (GTPHP5yr), 
and USD-denominated Philippine sovereign debt (GTUSDPH5Y). These provide duration exposure and EM credit risk.

\\section{Next Steps}

With this asset class mapping complete, we will proceed to:

\\begin{enumerate}
    \\item Implement data cleaning and currency normalization
    \\item Perform exploratory analysis to identify correlations and regime changes
    \\item Design signal prototypes for each asset class
    \\item Apply hierarchical risk parity within our risk budget framework
\\end{enumerate}

\\end{document}
"""
    
    return latex

def main():
    """Generate and save LaTeX files."""
    # Save just the tables
    with open('asset_class_table.tex', 'w') as f:
        f.write(generate_asset_class_table())
    
    with open('risk_budget_table.tex', 'w') as f:
        f.write(generate_risk_budget_table())
    
    # Save the full document
    with open('asset_class_mapping.tex', 'w') as f:
        f.write(generate_full_latex_document())
    
    print("LaTeX tables and document generated successfully.")
    print("Files saved: asset_class_table.tex, risk_budget_table.tex, asset_class_mapping.tex")

if __name__ == "__main__":
    main()

```

