# Databricks notebook source
#imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr
from pyspark.sql.functions import col,isnan,when,count
from pyspark.sql.functions import *

# COMMAND ----------

#Setting up the environment 
spark=SparkSession.builder.appName("Flipkart Data Engineering").getOrCreate()

# COMMAND ----------

#Load the CSV Data
file_path='/Volumes/workspace/default/flipkart/Flipkart.csv'

flipkart_df=spark.read.csv(file_path,header=True,inferSchema=True)
flipkart_df.display()

# COMMAND ----------

#checking the Schema

flipkart_df.printSchema()

flipkart_df.describe().show()

# COMMAND ----------

#handling the missing data

flipkart_df.select([count(when(col(c).isNull(), c)).alias(c) for c in flipkart_df.columns]).display()

#drop the rows that is missing 
flipkart_df_clean=flipkart_df.dropna()


#filling specific values to the nan columns or missing columns
flipkart_df_filled=flipkart_df.fillna({"Rating":0,"maincateg":"Men"})

# COMMAND ----------

# Data Transformation

# If 'Discount' column does not exist, set it to 0 or use the correct column name
if 'Discount' not in flipkart_df.columns:
    flipkart_df = flipkart_df.withColumn("Discount", expr("0"))

# Calculate the effective price after discount
flipkart_df_transformed = flipkart_df.withColumn(
    "EffectivePrice",
    expr("actprice1 - (actprice1 * Discount / 100)")
)

# Show the updated DataFrame
display(
    flipkart_df_transformed.select(
        "title",
        "actprice1",
        "Discount",
        "EffectivePrice"
    ),
    5
)

# COMMAND ----------

# Filter products with ratings greater than 4 and priced below 1000
high_rated_products = flipkart_df_filled.filter((col("Rating") > 4) )

# Show the result
high_rated_products.display(5)

# COMMAND ----------

#group by the category and calculte the average rating 

avg_rating_by_category=flipkart_df_filled.groupBy("maincateg").avg("Rating")
avg_rating_by_category.display()

# COMMAND ----------

#Total  Revenue by category 

total_revenue_by_category=flipkart_df_filled.groupBy("maincateg").agg(sum("Rating"))
total_revenue_by_category.display()

# COMMAND ----------

#Save the Processed Data

output_table='Flipkart_Data_Analysis_table'
flipkart_df_filled.write.mode("overwrite").saveAsTable(output_table)

# COMMAND ----------

# MAGIC %sql 
# MAGIC select * from Flipkart_Data_Analysis_table limit 20 

# COMMAND ----------

