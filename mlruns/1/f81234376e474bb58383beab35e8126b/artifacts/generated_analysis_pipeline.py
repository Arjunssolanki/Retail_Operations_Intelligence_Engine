import pandas as pd

try:
    sales
except NameError:
    sales = pd.read_csv("sales.csv")

try:
    customers
except NameError:
    customers = pd.read_csv("customers.csv")

# Calculate total spending per customer
customer_spending = (
    sales.groupby("Customer_ID")["Total_Revenue"].sum().reset_index()
)

# Get top 3 spending customers
top_3_spending = customer_spending.sort_values(
    by="Total_Revenue", ascending=False
).head(3)

# Merge with customers dataframe to include Customer_Name and City
result = top_3_spending.merge(customers, on="Customer_ID")[
    ["Customer_ID", "Customer_Name", "City", "Total_Revenue"]
]