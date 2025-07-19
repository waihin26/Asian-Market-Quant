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
