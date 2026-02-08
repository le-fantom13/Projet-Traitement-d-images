#!/usr/bin/env python3
"""
Lancement du système de gestion de péremption alimentaire
API Flask + simulation scanner IoT
"""

import os
from src.backend.app import app  # On importe l'objet Flask depuis app.py

# Dossier contenant les images
IMAGES_DIR = os.path.join("data", "images")

# Vérification du dataset
if not os.path.exists(IMAGES_DIR):
    raise FileNotFoundError(
        f"Dataset introuvable à {IMAGES_DIR}. "
        "Vérifie que le dossier data/images existe et contient des images."
    )

# Message de démarrage
print("✅ Dataset chargé avec succès")
print(f"🌐 Nombre d'images détectées : {len([f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png','.jpg','.jpeg'))])}")
print("🚀 Système de gestion de péremption alimentaire démarré")
print("🌐 Ouvrir http://127.0.0.1:5000 dans le navigateur")

# Lancement du serveur Flask
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
