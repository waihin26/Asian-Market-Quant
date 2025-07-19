# Asian Market Quant Project - Quick Start Guide

This guide provides step-by-step instructions to complete the first task of the project: **Scoping & Asset-Class Mapping**.

## Step 1: Setup Your Environment

First, ensure you have all necessary dependencies installed:

```bash
# Install required Python packages
pip install pandas numpy matplotlib seaborn openpyxl xlrd jupyter
```

Or simply use the requirements file:

```bash
pip install -r requirements.txt
```

## Step 2: Prepare Your Excel File

1. Place your Excel file containing the market data in a known location
2. Run the preparation script to analyze the file structure:

```bash
python prepare_excel.py path/to/your/excel_file.xlsx
```

This will:

- Copy your file to the `data/raw` directory
- Analyze the column headers to identify ticker types
- Display sample data to confirm the format

## Step 3: Process the Data and Create Asset Class Mapping

Choose one of these two methods:

### Option 1: Using the Python Script

```bash
python main.py data/raw/your_excel_file.xlsx
```

This will:

- Load your data from Excel
- Categorize the tickers into asset classes
- Generate LaTeX tables for reporting
- Save processed data files for future steps

### Option 2: Using the Jupyter Notebook

```bash
jupyter notebook notebooks/01_asset_class_mapping.ipynb
```

This provides an interactive experience where you can:

- Follow along with detailed explanations
- Visualize the asset class distribution
- Modify the risk budget allocation if needed
- Generate reports with your customizations

## Step 4: Review the Results

After running either option, you'll have:

1. **Processed Data Files** in `data/processed/`

   - `all_assets.xlsx` - The full dataset
   - `all_assets.pkl` - Pickled version for faster loading
   - Individual asset class files (e.g., `emerging_asia_equity.pkl`)
   - `data_dictionary.xlsx` - Documentation of all data fields

2. **LaTeX Reports** in `output/latex/`

   - `asset_class_mapping.tex` - Complete LaTeX document
   - `asset_class_table.tex` - Just the asset mapping table
   - `risk_budget_table.tex` - Just the risk budget table

3. **Tables** in `output/tables/`
   - CSV files containing the mapping data

## Step 5: Generate the Final Report

If you have LaTeX installed, you can generate the PDF report:

```bash
cd output/latex
pdflatex asset_class_mapping.tex
```

## Next Steps

After completing this first task, you're ready to move on to:

1. **Data Engineering Pipeline**: Currency normalization, corporate actions, etc.
2. **Exploratory Analysis**: Calculate summary statistics and correlations
3. **Signal Design**: Develop trading signals for each asset class

For any issues or questions, refer to the full documentation in the README.md file.
