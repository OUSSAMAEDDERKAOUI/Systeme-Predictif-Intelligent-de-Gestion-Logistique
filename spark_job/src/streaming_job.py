from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, current_timestamp
from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType, TimestampType
from pyspark.ml import PipelineModel

#  Configuration Spark
spark = SparkSession.builder \
    .appName("DataCoRealTime") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType() \
    .add("order_id", IntegerType()) \
    .add("order_city", StringType()) \
    .add("shipping_mode", StringType()) \
    .add("sales", DoubleType()) \
    .add("days_for_shipping_real", IntegerType()) \
    .add("days_for_shipment_scheduled", IntegerType()) \
    .add("timestamp", StringType()) # On le lit en string puis cast

#  Charger le modèle ML (Entraîné en Partie 1)
try:
    model_path = "/app/models/random_forest_model" # Chemin dans Docker
    model = PipelineModel.load(model_path)
    print("✅ Modèle chargé avec succès.")
except Exception as e:
    print("⚠️ Attention: Modèle non trouvé. Assurez-vous d'avoir exécuté la Partie 1.")
    model = None

#  Lire le Flux (Socket)
raw_stream = spark.readStream \
    .format("socket") \
    .option("host", "dataco-fastapi") \
    .option("port", 9999) \
    .load()

#  Parsing et Transformation
df_parsed = raw_stream.select(from_json(col("value"), schema).alias("data")).select("data.*")
df_clean = df_parsed.withColumn("timestamp", col("timestamp").cast(TimestampType()))

#  Prédiction (Si le modèle existe)
if model:
    df_final = model.transform(df_clean)
else:
    df_final = df_clean.withColumn("prediction", col("days_for_shipping_real") > col("days_for_shipment_scheduled"))

# --- FONCTION D'ÉCRITURE (Dual Write) ---
def write_to_databases(batch_df, batch_id):
    print(f"--- Traitement du Batch {batch_id} ---")
    
    # A. Stocker Raw + Prédiction dans PostgreSQL
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://dataco-postgres:5432/dataco_db") \
        .option("dbtable", "realtime_predictions") \
        .option("user", "user") \
        .option("password", "password") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()
    
    # B. Agréger pour MongoDB (Windowing)
    agg_df = batch_df \
        .groupBy(window(col("timestamp"), "30 seconds"), "order_city") \
        .agg({"prediction": "sum", "sales": "avg"}) \
        .withColumnRenamed("sum(prediction)", "total_delays") \
        .withColumnRenamed("avg(sales)", "avg_sales")
    
    # Écrire dans MongoDB
    agg_df.write \
        .format("mongo") \
        .option("uri", "mongodb://admin:password@dataco-mongodb:27017/dataco_db.city_stats?authSource=admin") \
        .mode("append") \
        .save()

#  Lancer le Stream
query = df_final.writeStream \
    .foreachBatch(write_to_databases) \
    .outputMode("update") \
    .start()

query.awaitTermination()