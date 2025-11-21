# # Fichier: spark_job/Dockerfile
# FROM python:3.10-slim-bullseye

# # Installation de Java (pour Spark)
# RUN apt-get update && \
#     apt-get install -y default-jre-headless && \
#     rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# # Copie tout (src/, notebooks/, etc.) dans le conteneur
# COPY . .

# # Expose le port de Jupyter
# EXPOSE 8888

# # Commande par défaut : lancer Jupyter Lab
# # On autorise l'accès depuis l'extérieur (0.0.0.0) et en tant que root
# CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]



# Fichier: spark_job/Dockerfile
FROM python:3.10-slim-bullseye

# 1. Installation de Java ET de curl (Nécessaire pour télécharger les Jars)
RUN apt-get update && \
    apt-get install -y default-jre-headless curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# --- NOUVEAU : TÉLÉCHARGEMENT DES DRIVERS (JARS) ---
# On crée le dossier et on télécharge les fichiers nécessaires pour Postgres et Mongo
RUN mkdir -p /app/jars

# Postgres JDBC
RUN curl -o /app/jars/postgresql-42.2.18.jar https://repo1.maven.org/maven2/org/postgresql/postgresql/42.2.18/postgresql-42.2.18.jar

# Mongo Spark Connector (Compatible Spark 3.x / Scala 2.12)
RUN curl -o /app/jars/mongo-spark-connector_2.12-3.0.1.jar https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/3.0.1/mongo-spark-connector_2.12-3.0.1.jar

# Mongo Java Driver (Dépendance requise)
RUN curl -o /app/jars/mongo-java-driver-3.12.10.jar https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/3.12.10/mongo-java-driver-3.12.10.jar

# ---------------------------------------------------

# Copie tout (src/, notebooks/, etc.) dans le conteneur
COPY . .

# Expose le port de Jupyter et l'UI Spark
EXPOSE 8888
EXPOSE 4040

# Commande par défaut
# # Commande par défaut : lancer Jupyter Lab
# # On autorise l'accès depuis l'extérieur (0.0.0.0) et en tant que root
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]