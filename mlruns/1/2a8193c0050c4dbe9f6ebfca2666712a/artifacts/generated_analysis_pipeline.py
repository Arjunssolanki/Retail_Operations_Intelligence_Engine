import pandas as pd

# Load the datasets
sales = pd.read_csv("sales.csv")
products = pd.read_csv("products.csv")

# Merge sales data with product details
merged_df = pd.merge(sales, products, on="Product_ID", how="inner")

# Generate the Product Performance Matrix
result = (
    merged_df.groupby(["Product_ID", "Product_Name", "Category"])
    .agg(
        Total_Quantity_Sold=("Quantity", "sum"),
        Total_Revenue=("Total_Revenue", "sum"),
        Average_Rating=("Rating", "mean"),
        Total_Transactions=("Invoice_ID", "nunique"),
    )
    .reset_index()
)