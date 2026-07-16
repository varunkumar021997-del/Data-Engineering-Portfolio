from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    name="retail_q.retail_silver.transactions",
    comment="Retail transaction data with proper typing and data quality checks"
)
@dp.expect_or_drop("non-null transaction_id", "transaction_id IS NOT NULL")
@dp.expect_or_drop("non-null opportunity_name", "opportunity_name IS NOT NULL")
@dp.expect("valid quantity", "quantity > 0")
@dp.expect("valid selling_price", "selling_price >= 0")
@dp.expect("valid discount_amount", "discount_amount >= 0")
@dp.expect("valid sales_channel", "sales_channel IN ('Store', 'Online')")
def transactions_clean():
    # Read source table as batch (materialized view)
    source_df = spark.read.table("retail_q.blob_bronze.transactions")
    
    # Transform and type the data properly
    return source_df.select(
        # Keep IDs as strings
        F.col("transaction_id"),
        F.trim(F.col("opportunity_name")).alias("opportunity_name"),
        F.col("product_id"),
        F.col("store_id"),
        
        # Convert quantity to integer
        F.col("quantity").cast("int").alias("quantity"),
        
        # Convert prices to decimal
        F.col("selling_price").cast("decimal(10,2)").alias("selling_price"),
        F.col("discount_amount").cast("decimal(10,2)").alias("discount_amount"),
        
        # Parse timestamp - handle format "DD-MMM-YYYY HH.MM.SS AM/PM"
        F.to_timestamp(F.col("transaction_timestamp"), "dd-MMM-yyyy hh.mm.ss a").alias("transaction_timestamp"),
        
        # Keep categorical fields
        F.col("payment_mode"),
        F.col("sales_channel")
    )
