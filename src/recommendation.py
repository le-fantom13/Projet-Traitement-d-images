import requests
import json

<<<<<<< HEAD
API_KEY = "Ta clé API Gemini"
=======
API_KEY = "AIzaSyCvsrA_6uO5DP9EC3xk-mCf3aZmJSC7k6I"
>>>>>>> 8099031 (Amélioration Frontend et Migration Paddle)
# On utilise l'un des modèles confirmés par ton diagnostic
MODEL = "gemini-flash-latest" 
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def assistant_llm(product_name, status):
    if "périmé" in status.lower():
        user_msg = f"Le produit {product_name} est périmé. Donne 2 risques sanitaires brefs et une consigne de tri."
    elif "alerte gaspillage" in status.lower():
        user_msg = f"Le produit {product_name} expire bientôt. Propose une idée de recette anti-gaspi ultra rapide."
    else:
        return "Produit encore consommable. Pensez à le ranger correctement !"

    payload = {
        "contents": [{
            "parts": [{"text": user_msg}]
        }]
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        res_json = response.json()

        if response.status_code == 200:
            # Extraction du texte selon la structure Gemini
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"Erreur API : {res_json}")
            return f"Service indisponible (Code {response.status_code})"

    except Exception as e:
        return f"Erreur de connexion : {str(e)}"
<<<<<<< HEAD
=======
    
>>>>>>> 8099031 (Amélioration Frontend et Migration Paddle)
