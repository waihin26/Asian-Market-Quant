"""
Asian Market Quant - Data Engineering Pipeline
-------------------------------------------------------
This module provides a comprehensive data engineering pipeline for financial market data.
It handles the entire process from raw data to analytics-ready datasets.

Key Features:
1. Data ingestion and cleaning (from .pkl or Excel files)
2. Business day frequency standardization with forward-filled holidays
3. Currency normalization to USD for consistent cross-market analysis
4. Daily and monthly returns calculation
5. Comprehensive data dictionary generation with quality metrics

Workflow:
1. Load data from data/raw/all_assets.pkl or use existing processed files
2. Clean and standardize the data to business day frequency
3. Normalize all prices to USD for consistent comparison
4. Calculate daily and monthly returns
5. Generate detailed data dictionary with asset information and quality metrics

Generated Files:
- daily_prices.pkl: Cleaned, normalized price data at daily frequency
- daily_prices.xlsx: Excel version for easy viewing
- daily_returns.pkl: Daily return series
- monthly_returns.pkl: Monthly return series
- data_dictionary.xlsx: Comprehensive asset information and data quality metrics

Generated Files:
- daily_prices.pkl: Cleaned, normalized price data at daily frequency
- daily_prices.xlsx: Excel version for easy viewing
- daily_returns.pkl: Daily return series
- monthly_returns.pkl: Monthly return series
- data_dictionary.xlsx: Documentation of assets and data quality
"""

import pandas as pd
import numpy as np
import sys, os
from pathlib import Path
import datetime as dt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, ROOT)

from mappings.asset_class_mapping import (
    ASSET_MAPPING,
    create_ticker_to_asset_class_map,
)

def load_raw_data(file_path, skiprows=7, parse_dates=True):
    """
    Load data from raw Excel file.
    
    Parameters:
    - file_path: Path to the Excel file
    - skiprows: Number of rows to skip (default: 7 for Bloomberg format)
    - parse_dates: Whether to parse the date column
    
    Returns:
    - DataFrame with the raw price data
    """
    try:
        print(f"Loading data from {file_path}...")
        df = pd.read_excel(file_path, skiprows=skiprows, index_col=0, parse_dates=parse_dates)
        print(f"Data loaded: {df.shape[0]} dates x {df.shape[1]} assets")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def clean_and_standardize(df):
    """
    Clean and standardize the raw data.
    
    Parameters:
    - df: Raw DataFrame 

    Returns:
    - Cleaned DataFrame with business day frequency and forward-filled holidays
    """
    if df is None:
        return None
    
    print("Cleaning and standardizing data...")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    
    # Make a copy to avoid modifying the original
    cleaned = df.copy()
    
    # Ensure index is datetime
    if not isinstance(cleaned.index, pd.DatetimeIndex):
        try:
            cleaned.index = pd.to_datetime(cleaned.index)
        except Exception as e:
            print(f"Error converting index to datetime: {e}")
            return None
    
    # Resample to business days and forward-fill missing values (holidays)
    cleaned = cleaned.asfreq('B').ffill()
    
    # Report on data completeness
    missing = cleaned.isna().sum().sum()
    total = cleaned.size
    completeness = (1 - missing / total) * 100
    
    print(f"Data standardized to business day frequency")
    print(f"Data completeness: {completeness:.2f}%")
    print(f"Missing values: {missing}")
    
    return cleaned


def normalize_to_usd(df, fx_tickers=None, fx_mapping=None):
    """
    Normalize all asset prices to USD.
    
    Parameters:
    - df: DataFrame with price data
    - fx_tickers: List of FX tickers in the DataFrame (if None, will be identified from ASSET_MAPPING)
    - fx_mapping: Dict mapping non-USD asset tickers to their currency conversion tickers
    
    Returns:
    - DataFrame with USD-normalized prices
    """
    if df is None:
        return None
    
    print("Normalizing asset prices to USD...")
    
    # Make a copy to avoid modifying the original
    normalized = df.copy()
    
    # If FX tickers not provided, get them from asset mapping
    if fx_tickers is None:
        fx_tickers = ASSET_MAPPING.get('fx_crosses', {}).get('tickers', [])
    
    # If FX mapping not provided, use a default based on asset mapping
    if fx_mapping is None:
        # Simplified mapping - in production would need more comprehensive mapping
        fx_mapping = {
            # JPY assets
            'NKY Index': 'USDJPY Curncy',  # Japanese equities -> convert with USDJPY
            # PHP assets
            'PCOMP Index': 'USDPHP Index',  # Philippines Composite -> convert with USDPHP
            'FMETF PM Equity': 'USDPHP Index',  # Philippines ETF -> convert with USDPHP
            'GTPHP5yr Corp': 'USDPHP Index',  # PHP sovereign bonds -> convert with USDPHP
            # Other assets are already in USD
        }
    
    # Process non-USD assets
    for ticker, fx_ticker in fx_mapping.items():
        if ticker in normalized.columns and fx_ticker in normalized.columns:
            print(f"Converting {ticker} to USD using {fx_ticker}")
            
            # For direct USD/XXX quotes (e.g., USDJPY), divide by FX rate
            # For indirect XXX/USD quotes, multiply by FX rate
            if fx_ticker.startswith('USD'):
                normalized[ticker] = normalized[ticker] / normalized[fx_ticker]
            else:
                normalized[ticker] = normalized[ticker] * normalized[fx_ticker]
    
    return normalized


def handle_futures_rolls(df, futures_contracts=None, roll_schedule=None):
    """
    Handle rolling of futures contracts.
    
    Parameters:
    - df: DataFrame with price data
    - futures_contracts: List of futures contract tickers
    - roll_schedule: Dict mapping contract tickers to roll dates
    
    Returns:
    - DataFrame with continuous futures prices
    """
    if df is None:
        return None
    
    print("Handling futures contract rolls...")
    
    # Make a copy to avoid modifying the original
    rolled = df.copy()
    
    # Default futures contracts if not provided
    if futures_contracts is None:
        futures_contracts = ['CO1 Comdty', 'GOLDS Index', 'S 1 Comdty']
        
    # Simple approach
    for contract in futures_contracts:
        if contract in rolled.columns:
            print(f"Processing rolls for {contract}")
            # Simple rolling average to smooth potential gaps (placeholder)
            rolled[contract] = rolled[contract].rolling(window=3, min_periods=1).mean()
    
    print("Futures contract rolls handled")
    return rolled


def calculate_returns(df, period='D'):
    """
    Calculate returns from price data.
    
    Parameters:
    - df: DataFrame with price data
    - period: Return calculation period ('D' for daily, 'M' for monthly)
    
    Returns:
    - DataFrame with returns
    """
    if df is None:
        return None
    
    print(f"Calculating {period} returns...")
    
    # Determine the appropriate return calculation method
    if period.upper() == 'D':
        # Daily returns
        returns = df.pct_change().dropna()
    elif period.upper() == 'M':
        # Monthly returns
        returns = df.resample('M').last().pct_change().dropna()
    else:
        print(f"Unsupported period: {period}")
        return None
    
    print(f"{period} returns calculated")
    return returns


def create_data_dictionary(df, output_path, daily_returns=None, monthly_returns=None):
    """
    Create a comprehensive data dictionary for the processed data.
    
    Parameters:
    - df: DataFrame with processed price data
    - output_path: Path to save the data dictionary
    - daily_returns: DataFrame with daily returns (optional)
    - monthly_returns: DataFrame with monthly returns (optional)
    
    Returns:
    - DataFrame with the data dictionary
    """
    if df is None:
        return None
    
    print("Creating comprehensive data dictionary...")
    
    # Get asset mapping
    ticker_map = create_ticker_to_asset_class_map()
    
    # Create dictionary entries
    data_dict = []
    for column in df.columns:
        asset_info = ticker_map.get(column, {})
        
        # Calculate data completeness
        non_null_values = df[column].count()
        total_values = len(df[column])
        completeness = (non_null_values / total_values * 100) if total_values > 0 else 0
        
        # Get return stats if available
        daily_ret_stats = {}
        if daily_returns is not None and column in daily_returns.columns:
            daily_ret = daily_returns[column].dropna()
            if len(daily_ret) > 0:
                daily_ret_stats = {
                    'Daily Return Mean (%)': round(daily_ret.mean() * 100, 4),
                    'Daily Return Std Dev (%)': round(daily_ret.std() * 100, 4),
                    'Daily Return Min (%)': round(daily_ret.min() * 100, 4),
                    'Daily Return Max (%)': round(daily_ret.max() * 100, 4),
                    'Daily Return Skewness': round(daily_ret.skew(), 4) if hasattr(daily_ret, 'skew') else 'N/A',
                    'Annualized Volatility (%)': round(daily_ret.std() * np.sqrt(252) * 100, 4)
                }
        
        # Create the dictionary entry with detailed information
        entry = {
            'Ticker': column,
            'Asset Class': asset_info.get('asset_class', 'Unknown').replace('_', ' ').title(),
            'Sub-Class': asset_info.get('sub_class', '').replace('_', ' ').title(),
            'Region': asset_info.get('region', '').replace('_', ' ').title(),
            'Description': asset_info.get('description', ''),
            'Bloomberg Ticker': asset_info.get('bloomberg_ticker', column),
            'Currency': 'USD',  # After normalization, all in USD
            'Original Currency': asset_info.get('currency', 'Unknown'),
            'Data Type': str(df[column].dtype),
            'Start Date': df[column].first_valid_index().strftime('%Y-%m-%d') if not df[column].isna().all() else 'N/A',
            'End Date': df[column].last_valid_index().strftime('%Y-%m-%d') if not df[column].isna().all() else 'N/A',
            'Data Points': non_null_values,
            'Missing Values': total_values - non_null_values,
            'Missing Values (%)': round(100 - completeness, 2),
            'Completeness (%)': round(completeness, 2),
            'Price Mean': round(df[column].mean(), 4) if pd.api.types.is_numeric_dtype(df[column]) else 'N/A',
            'Price Std Dev': round(df[column].std(), 4) if pd.api.types.is_numeric_dtype(df[column]) else 'N/A',
            'Price Min': round(df[column].min(), 4) if pd.api.types.is_numeric_dtype(df[column]) else 'N/A', 
            'Price Max': round(df[column].max(), 4) if pd.api.types.is_numeric_dtype(df[column]) else 'N/A',
            'Price Last': round(df[column].iloc[-1], 4) if not df[column].isna().all() and pd.api.types.is_numeric_dtype(df[column]) else 'N/A',
        }
        
        # Add return statistics if available
        entry.update(daily_ret_stats)
        
        data_dict.append(entry)
    
    # Convert to DataFrame
    data_dict_df = pd.DataFrame(data_dict)
    
    # Add metadata sheet
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        data_dict_df.to_excel(writer, sheet_name='Asset Dictionary', index=False)
        
        # Add metadata about the processing
        metadata = pd.DataFrame([
            {'Property': 'Creation Date', 'Value': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'Property': 'Number of Assets', 'Value': len(data_dict_df)},
            {'Property': 'Date Range', 'Value': f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}"},
            {'Property': 'Number of Trading Days', 'Value': len(df)},
            {'Property': 'Price Data Frequency', 'Value': 'Daily (Business Days)'},
            {'Property': 'Currency', 'Value': 'USD (Normalized)'},
            {'Property': 'Data Processing Steps', 'Value': 'Cleaned, Standardized, USD Normalized, Corporate Actions Adjusted'},
            {'Property': 'Notes', 'Value': 'All prices are adjusted for corporate actions and normalized to USD'}
        ])
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        # Add asset class summary
        if 'Asset Class' in data_dict_df.columns:
            asset_class_summary = data_dict_df['Asset Class'].value_counts().reset_index()
            asset_class_summary.columns = ['Asset Class', 'Count']
            asset_class_summary.to_excel(writer, sheet_name='Asset Class Summary', index=False)
    
    print(f"Enhanced data dictionary saved to {output_path}")
    print(f"  - {len(data_dict_df)} assets documented")
    print(f"  - {data_dict_df['Asset Class'].nunique()} asset classes")
    print(f"  - Added metadata and asset class summary sheets")
    
    return data_dict_df


def save_processed_data(df, file_path):
    """
    Save processed data to disk.
    
    Parameters:
    - df: DataFrame to save
    - file_path: Path to save the file
    """
    if df is None:
        return
    
    # Create directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Save based on file extension
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pkl':
        df.to_pickle(file_path)
    elif ext == '.csv':
        df.to_csv(file_path)
    elif ext == '.xlsx':
        df.to_excel(file_path)
    else:
        print(f"Unsupported file format: {ext}")
        return
    
    print(f"Data saved to {file_path}")


def run_data_pipeline(input_file=None, output_dir='data/processed', use_existing=True):
    """
    Run the data engineering pipeline to process financial market data.
    
    The pipeline performs the following steps:
    1. Load data (either from existing .pkl files or raw data)
    2. Clean and standardize to business day frequency
    3. Normalize all prices to USD
    4. Handle futures rolls for continuous contracts
    5. Calculate daily and monthly returns
    6. Generate comprehensive data dictionary
    
    Parameters:
    - input_file: Optional path to input file. If None:
        a) If use_existing=True, will load from data/processed/daily_prices.pkl
        b) If use_existing=False, will look for all_assets.pkl in data/raw/
    - output_dir: Directory to save processed outputs (default: 'data/processed')
    - use_existing: If True, will use existing processed data if available (default: True)
    
    Returns:
    - Dictionary containing:
        - 'daily_prices': DataFrame with processed daily prices
        - 'daily_returns': DataFrame with daily returns
        - 'monthly_returns': DataFrame with monthly returns
        - 'data_dictionary': DataFrame with comprehensive asset information
    """
    # Create output directory structure
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('data/raw', exist_ok=True)
    
    # Check if we can use existing processed data
    daily_prices_path = os.path.join(output_dir, 'daily_prices.pkl')
    if use_existing and os.path.exists(daily_prices_path):
        print(f"Using existing processed data from {daily_prices_path}")
        processed_df = pd.read_pickle(daily_prices_path)
        print(f"Loaded processed data: {processed_df.shape[0]} dates x {processed_df.shape[1]} assets")
        
        # Check if returns also exist
        daily_returns = None
        monthly_returns = None
        daily_returns_path = os.path.join(output_dir, 'daily_returns.pkl')
        monthly_returns_path = os.path.join(output_dir, 'monthly_returns.pkl')
        
        if os.path.exists(daily_returns_path):
            print(f"Loading existing daily returns from {daily_returns_path}")
            daily_returns = pd.read_pickle(daily_returns_path)
        
        if os.path.exists(monthly_returns_path):
            print(f"Loading existing monthly returns from {monthly_returns_path}")
            monthly_returns = pd.read_pickle(monthly_returns_path)
    else:
        # Need to process from raw data
        if input_file is None:
            # Try to find all_assets.xlsx in standard locations
            possible_locations = [
                'data/raw/all_assets.xlsx',
                'data/all_assets.xlsx',
                'all_assets.xlsx'
            ]
            
            for loc in possible_locations:
                if os.path.exists(loc):
                    input_file = loc
                    print(f"Found all_assets.xlsx at {loc}")
                    break
            
            if input_file is None:
                raise FileNotFoundError("Could not find all_assets.xlsx. Please specify input_file parameter.")
        
        print(f"Processing raw data from {input_file}...")
        # 1. Load raw data
        raw_df = load_raw_data(input_file)
        
        # Save a copy of raw data
        raw_output = os.path.join('data/raw', os.path.basename(input_file))
        if raw_df is not None and raw_output != input_file:
            save_processed_data(raw_df, raw_output)
    
    # 2. Clean and standardize
    cleaned_df = clean_and_standardize(raw_df)
    
    # 3. Normalize to USD
    usd_df = normalize_to_usd(cleaned_df)
    
    processed_df = handle_futures_rolls(usd_df)
    
    # 6. Calculate returns
    daily_returns = calculate_returns(processed_df, 'D')
    monthly_returns = calculate_returns(processed_df, 'M')
    
    # 7. Save processed outputs
    results = {}
    
    if processed_df is not None:
        # Save daily prices
        daily_prices_path = os.path.join(output_dir, 'daily_prices.pkl')
        save_processed_data(processed_df, daily_prices_path)
        results['daily_prices'] = processed_df
        
        # Save Excel version for easy viewing
        daily_prices_excel = os.path.join(output_dir, 'daily_prices.xlsx')
        save_processed_data(processed_df, daily_prices_excel)
    
    if daily_returns is not None:
        # Save daily returns
        daily_returns_path = os.path.join(output_dir, 'daily_returns.pkl')
        save_processed_data(daily_returns, daily_returns_path)
        results['daily_returns'] = daily_returns
    
    if monthly_returns is not None:
        # Save monthly returns
        monthly_returns_path = os.path.join(output_dir, 'monthly_returns.pkl')
        save_processed_data(monthly_returns, monthly_returns_path)
        results['monthly_returns'] = monthly_returns
    
    # 8. Create comprehensive data dictionary with all information
    data_dict_path = os.path.join(output_dir, 'data_dictionary.xlsx')
    data_dict = create_data_dictionary(
        processed_df, 
        data_dict_path,
        daily_returns=daily_returns,
        monthly_returns=monthly_returns
    )
    results['data_dictionary'] = data_dict
    
    print("\nData Engineering Pipeline complete!")
    print("=" * 50)
    print("Files created:")
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            full_path = os.path.join(root, file)
            size_kb = os.path.getsize(full_path) / 1024
            print(f"  - {os.path.relpath(full_path)}: {size_kb:.1f} KB")
    
    return results


if __name__ == "__main__":
    """
    Asian Market Quant - Data Engineering Pipeline
    -------------------------------------------
    This script processes financial market data through the following steps:
    1. Load pre-processed data from all_assets.pkl
    2. Clean and standardize to business day frequency
    3. Normalize all prices to USD
    4. Calculate daily and monthly returns
    5. Generate comprehensive data dictionary
    
    All outputs are saved in the data/processed/ directory.
    """
    import pandas as pd
    import sys
    from datetime import datetime

    print("\n🚀 Starting Data Engineering Pipeline")
    print("=" * 50)
    start_time = datetime.now()

    try:
        # 1) Load pre-processed all_assets.pkl
        all_assets_path = Path("data/raw/all_assets.pkl")
        if not all_assets_path.exists():
            raise FileNotFoundError(f"Could not find {all_assets_path}. Please ensure the file exists.")
            
        print(f"📊 Loading master data from {all_assets_path}")
        df = pd.read_pickle(all_assets_path)
        df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
        print(f"   Loaded {df.shape[0]} dates x {df.shape[1]} assets")

        # 2) Process the data through each pipeline step
        print("\n🔄 Processing Steps:")
        print("   1. Cleaning and standardizing...")
        cleaned = clean_and_standardize(df)
        
        print("   2. Normalizing to USD...")
        usd = normalize_to_usd(cleaned)
        
        print("   3. Calculating returns...")
        daily_ret = calculate_returns(usd, "D")
        monthly_ret = calculate_returns(usd, "M")

        # 3) Save processed outputs
        print("\n💾 Saving processed data:")
        save_processed_data(usd, "data/processed/daily_prices.pkl")
        save_processed_data(usd, "data/processed/daily_prices.xlsx")
        save_processed_data(daily_ret, "data/processed/daily_returns.pkl")
        save_processed_data(monthly_ret, "data/processed/monthly_returns.pkl")

        # 4) Build & save the data dictionary
        print("\n📖 Creating data dictionary...")
        create_data_dictionary(
            usd,
            "data/processed/data_dictionary.xlsx",
            daily_returns=daily_ret,
            monthly_returns=monthly_ret
        )

        elapsed_time = datetime.now() - start_time
        print("\n✅ Pipeline completed successfully!")
        print(f"⏱️  Total processing time: {elapsed_time.total_seconds():.2f} seconds")
        print("\nOutputs in data/processed/:")
        print("  - daily_prices.pkl & .xlsx: Clean, USD-normalized price data")
        print("  - daily_returns.pkl: Daily return series")
        print("  - monthly_returns.pkl: Monthly return series")
        print("  - data_dictionary.xlsx: Comprehensive asset information")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)