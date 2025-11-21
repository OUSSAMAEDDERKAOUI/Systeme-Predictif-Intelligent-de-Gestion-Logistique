# Fichier: fastapi_app/Dockerfile
FROM python:3.10-slim-bullseye

WORKDIR /app

# Assurez-vous d'avoir créé le fichier requirements.txt dans ce dossier
COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY . .

# Port API (8000) et Port Socket TCP (9999)
EXPOSE 8000
EXPOSE 9999

# La commande de lancement sera gérée par docker-compose ou ici par défaut
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]