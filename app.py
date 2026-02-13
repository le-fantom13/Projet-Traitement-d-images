from flask import Flask, jsonify, request, render_template
from datetime import date
import os
from werkzeug.utils import secure_filename

# Tes imports actuels
from src.ocr.txt_extraction import extract_text
from src.ocr.dlc_extraction import extract_dlc
from src.ocr.status import check_expiry_status
from src.recommendation import assistant_llm

app = Flask(__name__)

# Dossier contenant les images
IMAGES_DIR = os.path.join("data", "images")
UPLOAD_DIR = os.path.join("data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- ROUTE POUR AFFICHER LA PAGE ---
@app.route('/')
def index():
    return render_template('index.html')

# --- ROUTE DE TRAITEMENT D’UN FICHIER EXISTANT ---
@app.route('/process/<image_name>')
def process_image_route(image_name):
    product_name = image_name.split('.')[0]
    image_path = os.path.join(IMAGES_DIR, image_name)
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image introuvable'}), 404

    try:
        text = extract_text(image_path)
        dlc = extract_dlc(text)
        status_label = check_expiry_status(dlc)
        status_class = "status-valide"
        if "Alerte" in status_label: status_class = "status-alerte"
        if "Périmé" in status_label: status_class = "status-perime"
        recommendation = assistant_llm(product_name, status_label)

        return jsonify({
            'raw_text': text[:100] + "..." if text else "Aucun texte",
            'dlc': dlc.strftime("%d/%m/%Y") if dlc else "Non détectée",
            'status': status_label,
            'status_class': status_class,
            'recommendation': recommendation
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- ROUTE POUR UPLOAD / CAMÉRA ---
@app.route('/process-upload', methods=['POST'])
def process_upload():
    if 'image' not in request.files:
        return jsonify({'error': 'Aucune image reçue'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    # On utilise le nom du fichier pour la recommandation
    product_name = os.path.splitext(filename)[0]

    try:
        text = extract_text(save_path)
        dlc = extract_dlc(text)
        status_label = check_expiry_status(dlc)
        status_class = "status-valide"
        if "Alerte" in status_label: status_class = "status-alerte"
        if "Périmé" in status_label: status_class = "status-perime"
        recommendation = assistant_llm(product_name, status_label)

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
