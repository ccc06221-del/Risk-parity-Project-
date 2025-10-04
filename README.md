# Risk Parity Portfolio Optimization

## Overview

This project implements a two-step risk parity portfolio optimization strategy for ETF assets. The model uses a hierarchical approach where two specified assets are first optimized using risk parity principles, then this combined portfolio is treated as a synthetic asset and optimized with the remaining assets.

## Methodology

### Two-Step Risk Parity Approach

1. **First Step**: Two specified assets (`513030.SH` and `513080.SH`) are optimized using risk parity to create a synthetic portfolio
2. **Second Step**: The synthetic portfolio is combined with the remaining 19 assets and optimized again using risk parity principles

### Key Features

- **Risk Parity Optimization**: Allocates weights such that each asset contributes equally to portfolio risk
- **Rolling Window Analysis**: 17 monthly periods from March 2024 to July 2025
- **No Short Selling**: All weights are constrained between 0 and 1
- **Fully Invested**: Portfolio weights sum to 100%

## Requirements

### Python Libraries
```python
pandas
numpy
scipy
openpyxl (for Excel file reading)
```

### Data File
- **File**: `ETF list price 200825.xlsm`
- **Sheet**: `etf price automation (2)`
- **Format**: Excel file with price data for 21 ETF assets
- **Columns**: A to V (21 assets)
- **Index**: Dates in first column

## Code Structure

### Data Loading & Cleaning
- Reads ETF price data from Excel file
- Cleans missing values and converts data to numeric format
- Sets datetime index for time series analysis

### Optimization Engine
- `calculate_risk_parity_weights()`: Core optimization function
- Uses SLSQP optimization method from scipy
- Objective: Equal risk contribution across assets
- Constraints: Full investment, no short selling

### Two-Step Optimization Process
1. **Asset Pair Optimization**: Calculates risk parity weights for two specified ETFs
2. **Synthetic Portfolio Creation**: Combines the two assets into a single portfolio
3. **Full Portfolio Optimization**: Optimizes synthetic portfolio with remaining 19 assets

### Output
- **CSV File**: `risk_parity_portfolio_results.csv`
- Contains weights for all 21 assets for each period
- Includes portfolio performance metrics (mean return and variance)

## Output Columns

- `End_Date`: Period end date (YYYY-MM-DD)
- `Portfolio_Mean_Return`: Portfolio average return for the period
- `Portfolio_Variance`: Portfolio variance for the period
- `Weight_[Asset Code]`: Weight allocation for each ETF asset

## Usage

1. Ensure the Excel data file is in the same directory
2. Run the script:
```bash
python risk_parity_model.py
```
3. Check the generated `risk_parity_portfolio_results.csv` for results

## Key Assumptions

1. **Data Frequency**: Uses monthly returns calculated from daily price data
2. **Covariance Estimation**: Uses sample covariance matrix of returns
3. **Rebalancing**: Monthly rebalancing at end of each period
4. **Transaction Costs**: Not considered in optimization
5. **Liquidity**: Assumes all assets can be traded at observed prices

## Optimization Details

### Risk Parity Objective
The optimization minimizes the squared difference between each asset's risk contribution and the target equal risk contribution:

```
min Σ(RC_i - Portfolio_Variance/n)²
```

Where:
- `RC_i` = Risk contribution of asset i
- `n` = Number of assets
- Constraints: Σw_i = 1, 0 ≤ w_i ≤ 1

### Performance Metrics
- **Mean Return**: Average portfolio return for each period
- **Variance**: Portfolio return variance for risk assessment

## Customization

To modify the two target assets:
```python
asset1 = 'YOUR_ASSET_CODE_1'
asset2 = 'YOUR_ASSET_CODE_2'
```

To change the analysis period:
```python
end_dates = pd.date_range(start='YYYY-MM-DD', end='YYYY-MM-DD', freq='M')
```

## Notes

- The model assumes stationarity in return distributions
- Results should be validated with out-of-sample testing
- Consider adding transaction cost constraints for practical implementation
- Regular covariance matrix updates are recommended for live trading
