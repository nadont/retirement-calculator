import streamlit as st
import pandas as pd
import plotly.express as px

# Set app title
st.title("Dynamic Retirement Planning Calculator")

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
current_salary = st.sidebar.number_input(f"Current Salary ({currency}, {frequency_label})", min_value=0.0, value=50000.0, step=1000.0)
salary_growth_rate = st.sidebar.slider("Annual Salary Growth Rate (%)", min_value=0.0, max_value=50.0, value=3.0)
current_savings = st.sidebar.number_input(f"Current Savings ({currency})", min_value=0.0, value=100000.0, step=1000.0)
investment_percentage = st.sidebar.slider("Percentage of Savings Allocated to Investments (%)", min_value=0, max_value=100, value=50, step=1)
current_investment_return = st.sidebar.number_input("Expected Annual Investment Return (%)", min_value=0.0, max_value=20.0, value=5.0)
debts = st.sidebar.number_input(f"Total Debts ({currency})", min_value=0.0, value=50000.0, step=1000.0)
cost_of_living = st.sidebar.number_input(f"Cost of Living ({currency}, {frequency_label})", min_value=0.0, value=20000.0, step=1000.0)
inflation_rate = st.sidebar.slider("Inflation Rate (%)", min_value=0.0, max_value=10.0, value=2.0)
savings_rate = st.sidebar.slider("Savings Rate (% of Salary)", min_value=0, max_value=100, value=20, step=1)
tax_rate = st.sidebar.slider("Tax Rate (% of Salary)", min_value=0, max_value=100, value=10, step=1)
withdrawal_rate = st.sidebar.slider("Withdrawal Rate (%)", min_value=1, max_value=10, value=4, step=1)


# Calculate Retirement Metrics
def calculate_years_to_retire(
    current_age,
    salary,
    savings,
    return_rate,
    debts,
    cost_of_living,
    save_rate,
    tax_rate,
    salary_growth_rate,
    inflation_rate,
    withdrawal_rate,
    investment_percentage,
    frequency,
):
    annual_return = (return_rate / 100)
    inflation_rate_decimal = inflation_rate / 100
    investment_percentage_decimal = investment_percentage / 100
    net_savings = savings - debts
    retirement_fund_needed = cost_of_living * frequency * (100 / withdrawal_rate)
    saving_rate_decimal = save_rate / 100
    tax_rate_decimal = tax_rate / 100
    salary_growth_rate_decimal = salary_growth_rate / 100
    years_needed = 0

    # Simulation loop to calculate years needed to retire
    while net_savings < retirement_fund_needed and years_needed < 100:
        taxed_salary = salary * frequency * (1 - tax_rate_decimal)
        annual_saving = (taxed_salary * saving_rate_decimal) / frequency
        investment_growth = net_savings * investment_percentage_decimal * annual_return
        net_savings += investment_growth + (annual_saving * frequency)
        
        # Adjust salary and cost of living for growth and inflation
        cost_of_living *= (1 + inflation_rate_decimal)
        retirement_fund_needed = cost_of_living * frequency * (100 / withdrawal_rate)
        salary *= (1 + salary_growth_rate_decimal)
        years_needed += 1

    retirement_age = current_age + years_needed

    return years_needed, retirement_age, retirement_fund_needed, net_savings

years_needed, retirement_age, retirement_fund_needed, final_savings = calculate_years_to_retire(
    current_age,
    current_salary,
    current_savings,
    current_investment_return,
    debts,
    cost_of_living,
    savings_rate,
    tax_rate,
    salary_growth_rate,
    inflation_rate,
    withdrawal_rate,
    investment_percentage,
    frequency,
)

# Display Results
st.header("Results")
st.metric("Years Needed to Retire", years_needed)
st.metric("Retirement Age", retirement_age)
st.metric(f"Retirement Fund Needed ({frequency_label})", f"{retirement_fund_needed:,.2f} {currency}")
st.metric(f"Final Savings at Retirement ({frequency_label})", f"{final_savings:,.2f} {currency}")

# Interactive Dashboard
st.header("Insights Dashboard")
# Prepare data for visualization
data = {
    "Year": [],
    "Age": [],
    "Savings": [],
    "Investment Growth": [],
    "Total": [],
    "Salary": [],
}
net_savings = current_savings - debts
salary = current_salary
cost_of_living = cost_of_living * frequency
investment_percentage_decimal = investment_percentage / 100

# Loop to populate the data
for year in range(1, years_needed + 1):
    age = current_age + year
    data["Year"].append(year)
    data["Age"].append(age)
    taxed_salary = salary * (1 - (tax_rate / 100))
    annual_saving = (taxed_salary * (savings_rate / 100)) / frequency
    investment_growth = net_savings * investment_percentage_decimal * (current_investment_return / 100)
    net_savings += investment_growth + (annual_saving * frequency)
    cost_of_living *= (1 + (inflation_rate / 100))
    salary *= (1 + (salary_growth_rate / 100))
    data["Savings"].append(annual_saving * frequency)
    data["Investment Growth"].append(investment_growth)
    data["Total"].append(net_savings)
    data["Salary"].append(salary)

df = pd.DataFrame(data)

# Plot the savings growth
fig = px.line(
    df,
    x="Year",
    y=["Savings", "Investment Growth", "Total"],
    title=f"Savings Growth Over Time ({frequency_label.capitalize()})",
    labels={"value": f"Amount ({currency})", "variable": "Type"},
    markers=True,
)
st.plotly_chart(fig)

# Retirement Fund Comparison
fig_pie = px.pie(
    names=["Final Savings", "Retirement Fund Needed"],
    values=[final_savings, retirement_fund_needed],
    title="Retirement Savings vs Target",
)
st.plotly_chart(fig_pie)

# Final Notes
st.info(
    "This app calculates your retirement age based on the years needed to retire. "
    "Choose between monthly or yearly calculations at the beginning for a tailored experience. "
    "Adjust the percentage of savings allocated to investments to explore different scenarios."
)
