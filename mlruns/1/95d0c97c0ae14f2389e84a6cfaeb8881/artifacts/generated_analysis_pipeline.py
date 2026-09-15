import pandas as pd

# Merge sales and products dataframes
df = sales.merge(products, on="Product_ID")
df["Date"] = pd.to_datetime(df["Date"])

# Identify unique years to calculate Market Growth Rate
years = sorted(df["Date"].dt.year.unique())

if len(years) >= 2:
    rev_earliest = (
        df[df["Date"].dt.year == years[0]]
        .groupby("Product_ID")["Total_Revenue"]
        .sum()
    )
    rev_latest = (
        df[df["Date"].dt.year == years[-1]]
        .groupby("Product_ID")["Total_Revenue"]
        .sum()
    )
    growth = (rev_latest - rev_earliest) / rev_earliest
else:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    mid_date = min_date + (max_date - min_date) / 2
    rev_earliest = (
        df[df["Date"] <= mid_date].groupby("Product_ID")["Total_Revenue"].sum()
    )
    rev_latest = (
        df[df["Date"] > mid_date].groupby("Product_ID")["Total_Revenue"].sum()
    )
    growth = (rev_latest - rev_earliest) / rev_earliest

# Calculate Total Revenue per Product
product_summary = (
    df.groupby(["Product_ID", "Product_Name", "Category"])["Total_Revenue"]
    .sum()
    .reset_index()
)
product_summary["Market_Growth_Rate"] = product_summary["Product_ID"].map(growth)

# Calculate Relative Market Share
max_rev = product_summary["Total_Revenue"].max()
product_summary["Relative_Market_Share"] = (
    product_summary["Total_Revenue"] / max_rev
)

# BCG Matrix Classification based on median thresholds
growth_threshold = product_summary["Market_Growth_Rate"].median()
share_threshold = product_summary["Relative_Market_Share"].median()


def assign_bcg(row):
    high_growth = row["Market_Growth_Rate"] >= growth_threshold
    high_share = row["Relative_Market_Share"] >= share_threshold
    if high_growth and high_share:
        return "Star"
    elif not high_growth and high_share:
        return "Cash Cow"
    elif high_growth and not high_share:
        return "Question Mark"
    else:
        return "Dog"


product_summary["BCG_Category"] = product_summary.apply(assign_bcg, axis=1)

result = product_summary