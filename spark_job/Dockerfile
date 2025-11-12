# Fichier: spark_job/Dockerfile
FROM python:3.10-slim-bullseye

# Installation de Java (pour Spark)
RUN apt-get update && \
    apt-get install -y default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copie tout (src/, notebooks/, etc.) dans le conteneur
COPY . .

# Expose le port de Jupyter
EXPOSE 8888

# Commande par défaut : lancer Jupyter Lab
# On autorise l'accès depuis l'extérieur (0.0.0.0) et en tant que root
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]