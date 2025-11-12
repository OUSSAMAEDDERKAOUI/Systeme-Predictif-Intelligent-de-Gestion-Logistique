# Image Python standard
FROM python:3.10-slim-bullseye

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
# AJOUTEZ BIEN --default-timeout=1000 ICI 👇
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copie du code de l'application
COPY . .

# Streamlit tourne par défaut sur le port 8501, on l'expose
EXPOSE 8501

# Commande pour lancer Streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]