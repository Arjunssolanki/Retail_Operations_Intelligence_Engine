import pandas as pd
import random
from datetime import datetime, timedelta
from io import StringIO
from s3_manager import S3DataLakeManager
from logger_config import get_logger

logger = get_logger("generate_and_upload_data")

def generate_big_retail_ecosystem():
    logger.info("Initializing high-volume relational retail data generation engine.")
    
    product_pool = [
        ("PROD-101", "Wireless Headphones", "Electronics", 89.99),
        ("PROD-102", "Mechanical Keyboard", "Electronics", 129.50),
        ("PROD-103", "Ergonomic Office Chair", "Furniture", 249.99),
        ("PROD-104", "LED Desk Lamp", "Furniture", 34.25),
        ("PROD-105", "Waterproof Backpack", "Travel Gear", 59.95),
        ("PROD-106", "Stainless Water Bottle", "Travel Gear", 24.99),
        ("PROD-107", "Organic Protein Powder", "Health & Wellness", 45.00),
        ("PROD-108", "Multivitamin Pack", "Health & Wellness", 19.99)
    ]
    products_df = pd.DataFrame(product_pool, columns=["Product_ID", "Product_Name", "Category", "Unit_Price"])
    
    first_names = ["Arjun", "Neha", "Rohan", "Priya", "Amit", "Ananya", "Vikram", "Sneha", "Kabir", "Meera"]
    last_names = ["Sharma", "Verma", "Gupta", "Mehta", "Joshi", "Nair", "Reddy", "Patel", "Singh", "Rao"]
    customer_types = ["Member", "Normal"]
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]
    
    logger.info("Generating 10,000 customer records...")
    customers_data = []
    for i in range(10000):
        customer_id = f"CUST-{10000 + i}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        c_type = random.choice(customer_types)
        city = random.choice(cities)
        customers_data.append([customer_id, name, c_type, city])
    customers_df = pd.DataFrame(customers_data, columns=["Customer_ID", "Customer_Name", "Customer_Type", "City"])
    
    payment_methods = ["Credit Card", "UPI", "Cash", "E-Wallet"]
    start_date = datetime(2026, 1, 1)
    
    logger.info("Generating 500,000 sales transactions records...")
    sales_data = []
    for i in range(500000):
        invoice_id = f"INV-{1000000 + i}"
        customer_id = f"CUST-{random.randint(10000, 19999)}"
        prod_tuple = random.choice(product_pool)
        product_id = prod_tuple[0]
        unit_price = prod_tuple[3]
        quantity = random.randint(1, 5)
        total_revenue = round(unit_price * quantity, 2)
        tx_date = (start_date + timedelta(days=random.randint(0, 240))).strftime("%Y-%m-%d")
        payment = random.choice(payment_methods)
        rating = round(random.uniform(5.0, 10.0), 1)
        
        sales_data.append([invoice_id, tx_date, customer_id, product_id, quantity, total_revenue, payment, rating])
        
    sales_df = pd.DataFrame(sales_data, columns=["Invoice_ID", "Date", "Customer_ID", "Product_ID", "Quantity", "Total_Revenue", "Payment_Method", "Rating"])
    
    logger.info("High-volume relational datasets successfully generated in system memory.")
    return customers_df, products_df, sales_df

def execute_relational_upload():
    try:
        customers_df, products_df, sales_df = generate_big_retail_ecosystem()
        datasets = {
            "products.csv": products_df,
            "customers.csv": customers_df,
            "sales.csv": sales_df
        }
        
        s3_manager = S3DataLakeManager()
        
        for file_name, df in datasets.items():
            df.to_csv(file_name, index=False)
            logger.info(f"Saved local relational big-data checkpoint: {file_name}")
            
            print(f"⏳ Syncing large asset '{file_name}' to AWS S3 bucket...")
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            
            s3_manager.s3_client.put_object(
                Bucket=s3_manager.bucket_name,
                Key=file_name,
                Body=csv_buffer.getvalue()
            )
            logger.info(f"Successfully uploaded large asset '{file_name}' to cloud data lake.")
            print(f"✅ Success! '{file_name}' is stored in your S3 bucket.")
            
        active_files = s3_manager.list_available_datasets()
        print(f"📋 Current active high-volume data lake catalog: {active_files}")
        
    except Exception as e:
        logger.critical(f"Pipeline scale-up upload operational failure: {str(e)}")
        print(f"❌ Target synchronization failure: {e}")

if __name__ == "__main__":
    execute_relational_upload()
