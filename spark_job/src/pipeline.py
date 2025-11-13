from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

# 1️⃣ Création de la Spark Session
spark = SparkSession.builder \
    .appName("DeliveryDelayPrediction") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

# 2️⃣ Chargement des données
df = spark.read.csv("data/delivery_data.csv", header=True, inferSchema=True)

# 3️⃣ Sélection des colonnes pertinentes
cols_to_use = [
    'Type',
    'Late_delivery_risk',
    'Customer Segment',
    'Order Region',
    'Order Item Quantity',
    'Product Price',
    'Sales',
    'Order Profit Per Order',
    'Shipping Mode',
    'Latitude',
    'Longitude'
]

df = df.select(cols_to_use)

# 4️⃣ Prétraitement : gestion des valeurs manquantes
df = df.na.drop()

# 5️⃣ Définition des variables catégorielles et numériques
categorical_cols = ['Type', 'Customer Segment', 'Order Region', 'Shipping Mode']
numeric_cols = ['Order Item Quantity', 'Product Price', 'Sales', 'Order Profit Per Order', 'Latitude', 'Longitude']

# 6️⃣ Indexation et encodage des variables catégorielles
indexers = [StringIndexer(inputCol=col, outputCol=col + "_idx", handleInvalid="keep") for col in categorical_cols]
encoders = [OneHotEncoder(inputCols=[col + "_idx"], outputCols=[col + "_ohe"]) for col in categorical_cols]

# 7️⃣ Assemblage des features
assembler_inputs = [col + "_ohe" for col in categorical_cols] + numeric_cols
assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="features")

# 8️⃣ Normalisation (optionnelle)
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")

# 9️⃣ Définition du modèle de classification
rf = RandomForestClassifier(
    featuresCol="scaled_features",
    labelCol="Late_delivery_risk",
    numTrees=100,
    maxDepth=10,
    seed=42
)

# 🔟 Construction du pipeline MLlib
pipeline = Pipeline(stages=indexers + encoders + [assembler, scaler, rf])

# 11️⃣ Séparation du dataset
train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

# 12️⃣ Entraînement du modèle
model = pipeline.fit(train_df)

# 13️⃣ Prédictions
predictions = model.transform(test_df)

# 14️⃣ Évaluation
evaluator = MulticlassClassificationEvaluator(
    labelCol="Late_delivery_risk",
    predictionCol="prediction",
    metricName="f1"
)

f1_score = evaluator.evaluate(predictions)
print(f"✅ F1-score du modèle : {f1_score:.4f}")

# 15️⃣ Sauvegarde du modèle
model.write().overwrite().save("models/logistics_rf_pipeline")

