import pandas as pd
import numpy as np
from scipy.optimize import minimize
import os

# Read the price data
file_path = "ETF list price 200825.xlsm"
price_data = pd.read_excel(
    file_path,git add .
git commit -m "Delete all files except risk parity model monthly risk parity optimization 270825.py"
git push origin master
    sheet_name='etf price automation (2)',
    header=1,
    index_col=0,
    usecols="A:V",
    skiprows=0
)

# Clean the data
price_data = price_data[price_data.index.notnull()]
price_data.index = pd.to_datetime(price_data.index, errors='coerce')
price_data = price_data.apply(pd.to_numeric, errors='coerce')

# Define the two assets for the first risk parity optimization
asset1 = '513030.SH'  # Adjust these codes based on your actual column names
asset2 = '513080.SH'  # Adjust these codes based on your actual column names

# Generate end dates for the 17 periods
end_dates = pd.date_range(start='2024-03-31', end='2025-07-31', freq='M')


# Function to calculate risk parity weights
def calculate_risk_parity_weights(cov_matrix):
    n = cov_matrix.shape[0]

    # Define the risk parity objective function
    def risk_parity_objective(weights):
        portfolio_variance = weights.T @ cov_matrix @ weights
        marginal_risk_contribution = cov_matrix @ weights
        risk_contribution = weights * marginal_risk_contribution / portfolio_variance

        # Objective: equal risk contribution
        target_risk_contribution = portfolio_variance / n
        return np.sum((risk_contribution - target_risk_contribution) ** 2)

    # Constraints: weights sum to 1, no short selling
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    bounds = [(0, 1) for _ in range(n)]

    # Initial guess (equal weights)
    x0 = np.ones(n) / n

    # Optimize
    result = minimize(risk_parity_objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)

    return result.x


# Prepare results storage
all_results = []

# Process each period
for i, end_date in enumerate(end_dates):
    print(f"Processing period ending {end_date.strftime('%Y-%m-%d')}")

    # Filter data up to the current end date
    period_data = price_data[price_data.index <= end_date]

    # Calculate returns
    returns = period_data.pct_change().dropna()

    # Calculate covariance matrix
    cov_matrix = returns.cov()

    # Step 1: Risk parity optimization for the two specified assets
    two_asset_indices = [returns.columns.get_loc(asset1), returns.columns.get_loc(asset2)]
    two_asset_cov = cov_matrix.iloc[two_asset_indices, two_asset_indices].values
    two_asset_weights = calculate_risk_parity_weights(two_asset_cov)

    # Create a synthetic asset representing the two-asset portfolio
    two_asset_portfolio_returns = returns[[asset1, asset2]] @ two_asset_weights

    # Step 2: Combine with the other 19 assets
    other_assets = [col for col in returns.columns if col not in [asset1, asset2]]
    combined_returns = returns[other_assets].copy()
    combined_returns['Two_Asset_Portfolio'] = two_asset_portfolio_returns

    # Calculate covariance matrix for the combined assets
    combined_cov = combined_returns.cov()

    # Risk parity optimization for the combined assets
    combined_weights = calculate_risk_parity_weights(combined_cov.values)

    # Map weights back to original assets
    final_weights = np.zeros(len(returns.columns))

    # Weight for the two-asset portfolio is distributed to the individual assets
    two_asset_portfolio_weight = combined_weights[-1]
    final_weights[two_asset_indices[0]] = two_asset_portfolio_weight * two_asset_weights[0]
    final_weights[two_asset_indices[1]] = two_asset_portfolio_weight * two_asset_weights[1]

    # Weights for the other assets
    for j, asset in enumerate(other_assets):
        asset_idx = returns.columns.get_loc(asset)
        final_weights[asset_idx] = combined_weights[j]

    # Calculate portfolio performance
    portfolio_returns = returns @ final_weights
    portfolio_mean_return = portfolio_returns.mean()
    portfolio_variance = portfolio_returns.var()

    # Store results
    result_dict = {
        'End_Date': end_date.strftime('%Y-%m-%d'),
        'Portfolio_Mean_Return': portfolio_mean_return,
        'Portfolio_Variance': portfolio_variance
    }

    # Add individual asset weights
    for j, asset in enumerate(returns.columns):
        result_dict[f'Weight_{asset}'] = final_weights[j]

    all_results.append(result_dict)

# Create DataFrame from results
results_df = pd.DataFrame(all_results)

# Save to CSV
results_df.to_csv('risk_parity_portfolio_results.csv', index=False)
print("Risk parity portfolio results saved to 'risk_parity_portfolio_results.csv'")

# Display summary
print("\nSummary of portfolio performance across all periods:")
print(f"Average portfolio return: {results_df['Portfolio_Mean_Return'].mean():.6f}")
print(f"Average portfolio variance: {results_df['Portfolio_Variance'].mean():.6f}")