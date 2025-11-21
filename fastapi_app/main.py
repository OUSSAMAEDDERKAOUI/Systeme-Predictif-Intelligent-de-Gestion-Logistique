import socket
import json
import time
import random
import threading
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

# Schéma de données simulé (Basé sur DataCo)
CITIES = ["Paris", "New York", "Tokyo", "Berlin", "London", "Casablanca"]
SHIPPING_MODES = ["Standard Class", "First Class", "Second Class", "Same Day"]

def generate_order():
    """Génère une commande aléatoire"""
    return {
        "order_id": random.randint(10000, 99999),
        "order_city": random.choice(CITIES),
        "shipping_mode": random.choice(SHIPPING_MODES),
        "sales": round(random.uniform(10.0, 500.0), 2),
        "days_for_shipping_real": random.randint(0, 6),
        "days_for_shipment_scheduled": random.randint(0, 4),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# --- Le Bridge TCP (Socket) ---
def start_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # On écoute sur toutes les interfaces du conteneur, port 9999
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print("🚀 Socket Server listening on port 9999...")

    while True:
        client, addr = server.accept()
        print(f"✅ Spark connected from {addr}")
        try:
            while True:
                data = generate_order()
                # Spark attend du texte avec un saut de ligne
                message = json.dumps(data) + "\n"
                client.send(message.encode('utf-8'))
                time.sleep(1) # Une commande par seconde
        except Exception as e:
            print(f"❌ Client disconnected: {e}")
            client.close()

# Lancer le socket en arrière-plan quand l'API démarre
@app.on_event("startup")
async def startup_event():
    t = threading.Thread(target=start_socket_server)
    t.daemon = True
    t.start()

@app.get("/")
def read_root():
    return {"status": "Data Generator is Running"}