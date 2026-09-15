import pandas as pd

try:
    sales_df = sales
except NameError:
    sales_df = pd.read_csv("sales.csv")

result = sales_df["Total_Revenue"].sum()