import streamlit as st
import pandas as pd
import plotly.express as px

# Set app title
st.title("Retirement Planning Calculator")

# Sidebar inputs
st.sidebar.header("Settings")
contribution_frequency = st.sidebar.radio(
    "Choose Calculation Frequency",
    ["Monthly", "Yearly"]
)
frequency_label = "per month" if contribution_frequency == "Monthly" else "per year"
frequency = 12 if contribution_frequency == "Monthly" else 1

# Sidebar user inputs
st.sidebar.header("User Input")
current_age = st.sidebar.number_input("Current Age", min_value=0, max_value=100, value=30)
currency = st.sidebar.selectbox("Currency", ["THB", "GBP"])
current_salary = st.sidebar.number_input(
    f"Current Salary ({currency}, {frequency_label})",
    min_value=0.0,
    value=50000.0,
    step=1000.0,
)

st.sidebar.header("Salary Allocation (%)")
debt_percentage = st.sidebar.slider("Debt Payment (%)", min_value=0, max_value=100, value=10, step=1)
investment_percentage = st.sidebar.slider("Investment (%)", min_value=0, max_value=100, value=30, step=1)
cost_of_living_percentage = st.sidebar.slider("Cost of Living (%)", min_value=0, max_value=100, value=40, step=1)
savings_percentage = st.sidebar.slider("Savings (%)", min_value=0, max_value=100, value=20, step=1)

# Validate that percentages add up to 100%
if debt_percentage + investment_percentage + cost_of_living_percentage + savings_percentage != 100:
    st.sidebar.error("The percentages must add up to 100%.")

# Additional financial inputs
salary_growth_rate = st.sidebar.slider("Annual Salary Growth Rate (%)", min_value=0.0, max_value=50.0, value=3.0)
current_savings = st.sidebar.number_input(f"Current Savings ({currency})", min_value=0.0, value=100000.0, step=1000.0)
investment_growth_rate = st.sidebar.number_input(
    "Expected Annual Investment Growth Rate (%)",
    min_value=0.0,
    max_value=20.0,
    value=5.0,
)
total_debt = st.sidebar.number_input(f"Total Debt ({currency})", min_value=0.0, value=200000.0, step=1000.0)
inflation_rate = st.sidebar.slider("Inflation Rate (%)", min_value=0.0, max_value=10.0, value=2.0)
withdrawal_rate = st.sidebar.slider("Withdrawal Rate (%)", min_value=1, max_value=10, value=4, step=1)

# New sidebar input for retirement cost of living
retirement_cost_of_living = st.sidebar.number_input(
    f"Retirement Cost of Living ({currency}, {frequency_label})",
    min_value=0.0,
    value=30000.0,
    step=1000.0,
)

# Function to calculate retirement metrics
def calculate_years_to_retire(
    current_age,
    salary,
    savings,
    investment_growth_rate,
    retirement_cost_of_living,
    debt_percentage,
    investment_percentage,
    savings_percentage,
    salary_growth_rate,
    inflation_rate,
    withdrawal_rate,
    total_debt,
    frequency,
):
    inflation_rate_decimal = inflation_rate / 100
    net_savings = savings
    net_investments = 0  # Separate investments
    debt_remaining = total_debt
    retirement_fund_needed = retirement_cost_of_living * frequency * (100 / withdrawal_rate)
    debt_allocation = debt_percentage / 100
    investment_allocation = investment_percentage / 100
    savings_allocation = savings_percentage / 100
    salary_growth_rate_decimal = salary_growth_rate / 100
    investment_growth_rate_decimal = investment_growth_rate / 100
    years_needed = 0

    # Tracking data for plotting
    data = {
        "Year": [],
        "Savings": [],
        "Investment Growth": [],
        "Total Debt": [],
        "Total": [],
    }

    # Simulation loop to calculate years needed to retire
    while debt_remaining > 0 or (net_savings + net_investments) < retirement_fund_needed and years_needed < 100:
        annual_salary = salary * frequency

        # Calculate allocations
        debt_payment = annual_salary * debt_allocation
        investment_contribution = annual_salary * investment_allocation
        annual_savings = annual_salary * savings_allocation

        # Reduce debt if still remaining
        if debt_remaining > 0:
            debt_remaining -= debt_payment
            debt_remaining = max(debt_remaining, 0)  # Ensure it doesn't go negative

        # Grow savings and investments concurrently
        net_savings += annual_savings
        net_investments += investment_contribution

        # Apply investment growth
        investment_growth = net_investments * investment_growth_rate_decimal
        net_investments += investment_growth

        # Adjust salary for growth
        salary *= (1 + salary_growth_rate_decimal)

        # Freeze retirement fund target once it has been met or exceeded
        if (net_savings + net_investments) >= retirement_fund_needed:
            retirement_fund_needed = retirement_fund_needed  # Freeze the target value

        # Adjust retirement fund target for inflation only if not frozen
        if (net_savings + net_investments) < retirement_fund_needed:
            retirement_fund_needed *= (1 + inflation_rate_decimal)

        # Record data for plotting
        total_savings = net_savings + net_investments
        data["Year"].append(current_age + years_needed)
        data["Savings"].append(net_savings)
        data["Investment Growth"].append(net_investments)
        data["Total Debt"].append(debt_remaining)
        data["Total"].append(total_savings)

        years_needed += 1

    retirement_age = current_age + years_needed
    df = pd.DataFrame(data)  # Convert tracking data to DataFrame
    return years_needed, retirement_age, retirement_fund_needed, net_savings, net_investments, debt_remaining, df


# Call the updated function
years_needed, retirement_age, retirement_fund_needed, final_savings, final_investments, remaining_debt, df = calculate_years_to_retire(
    current_age,
    current_salary,
    current_savings,
    investment_growth_rate,
    retirement_cost_of_living,
    debt_percentage,
    investment_percentage,
    savings_percentage,
    salary_growth_rate,
    inflation_rate,
    withdrawal_rate,
    total_debt,
    frequency,
)

# Display Results
st.header("Results")
st.metric("Years Needed to Retire", years_needed)
st.metric("Retirement Age", retirement_age)
st.metric(f"Retirement Fund Needed ({currency})", f"{retirement_fund_needed:,.2f}")
st.metric(f"Final Savings at Retirement ({currency})", f"{final_savings:,.2f}")
st.metric(f"Final Investments at Retirement ({currency})", f"{final_investments:,.2f}")
st.metric(f"Remaining Debt ({currency})", f"{remaining_debt:,.2f}")

# Plot the savings growth
fig = px.line(
    df,
    x="Year",
    y=["Savings", "Investment Growth", "Total Debt", "Total"],
    title=f"Financial Growth Over Time ({frequency_label.capitalize()})",
    labels={"value": f"Amount ({currency})", "variable": "Type"},
    markers=True,
)
st.plotly_chart(fig)

# Salary Allocation Bar Chart
st.header("Salary Allocation")
allocation_data = {
    "Category": ["Debt Payment", "Investment", "Cost of Living", "Savings"],
    "Percentage": [debt_percentage, investment_percentage, cost_of_living_percentage, savings_percentage],
}
allocation_df = pd.DataFrame(allocation_data).sort_values(by="Percentage")

fig_bar = px.bar(
    allocation_df,
    x="Percentage",
    y="Category",
    orientation="h",
    title="Salary Allocation Breakdown",
    labels={"Percentage": "Percentage (%)", "Category": "Allocation"},
)
st.plotly_chart(fig_bar)

# Final Notes
st.info(
    "This app calculates your retirement age based on the years needed to retire. "
    "Ensure that your salary allocations add up to 100%. Adjust parameters to explore different scenarios. "
    "Debt is reduced concurrently with investment growth and savings."
)
