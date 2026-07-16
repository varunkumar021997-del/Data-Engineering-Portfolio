# Read CSV files from volume using Auto Loader
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/retail_q/volumes/blob_source/_schema")
  .option("header", "true")
  .option("inferSchema", "true")
  .load("/Volumes/retail_q/volumes/blob_source/transactions_source/")
)

# Write to bronze table with trigger(availableNow=True) to process all files and exit
query = (df.writeStream
  .option("checkpointLocation", "/Volumes/retail_q/volumes/blob_source/_checkpoint")
  .trigger(availableNow=True)
  .toTable("retail_q.blob_bronze.transactions")
)

# Wait for the stream to finish processing all available data
query.awaitTermination()
print("Auto Loader ingestion completed successfully!")