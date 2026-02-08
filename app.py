from flask import Flask, jsonify, request, render_template
from datetime import date
import os

# Tes imports actuels (on garde tes noms de fichiers)
from src.ocr.txt_extraction import extract_text
from src.ocr.dlc_extraction import extract_dlc
from src.ocr.status import check_expiry_status
from src.recommendation import assistant_llm

app = Flask(__name__)

# Dossier contenant les images
IMAGES_DIR = os.path.join("data", "images")

# --- ROUTE POUR AFFICHER LA PAGE ---
@app.route('/')
def index():
    # S'assure que ton fichier HTML est dans un dossier nommé 'templates'
    return render_template('index.html')

# --- ROUTE POUR LISTER LES IMAGES (utilisée par ton fetch JS) ---
@app.route('/images')
def get_images():
    if not os.path.exists(IMAGES_DIR):
        return jsonify([])
    images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return jsonify(images)

# --- ROUTE DE TRAITEMENT (modifiée pour correspondre à ton JS) ---
@app.route('/process/<image_name>')
def process_image_route(image_name):
    product_name = image_name.split('.')[0] # On prend le nom sans l'extension
    image_path = os.path.join(IMAGES_DIR, image_name)
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image introuvable'}), 404

    try:
        # 1️⃣ OCR
        text = extract_text(image_path)

        # 2️⃣ Extraction DLC
        dlc = extract_dlc(text) 

        # 3️⃣ Statut produit (on récupère le texte pour l'affichage)
        status_label = check_expiry_status(dlc)
        
        # Petit ajustement pour que le CSS du HTML fonctionne (couleurs)
        status_class = "status-valide"
        if "Alerte" in status_label: status_class = "status-alerte"
        if "Périmé" in status_label: status_class = "status-perime"

        # 4️⃣ Assistant IA
        recommendation = assistant_llm(product_name, status_label)

        # On renvoie exactement ce que ton script JS attend
        return jsonify({
            'raw_text': text[:100] + "..." if text else "Aucun texte",
            'dlc': dlc.strftime("%d/%m/%Y") if dlc else "Non détectée",
            'status': status_label,
            'status_class': status_class,
            'recommendation': recommendation
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)