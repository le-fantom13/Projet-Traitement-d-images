import cv2
import re
import numpy as np
from paddleocr import PaddleOCR

# Initialisation ultra-simple (laisse Paddle gérer ses noms de paramètres)
ocr = PaddleOCR(lang='fr')

MONTHS = {
    "JAN": "01", "JANV": "01", "FEB": "02", "FEV": "02", "FÉV": "02",
    "MAR": "03", "MARS": "03", "APR": "04", "AVR": "04", "MAY": "05",
    "MAI": "05", "JUN": "06", "JUNS": "06", "JUI": "07", "JUL": "07",
    "AUG": "08", "AOU": "08", "AOÛ": "08", "SEP": "09", "OCT": "10",
    "NOV": "11", "DEC": "12", "DÉC": "12"
}

def preprocess(image_path):
    """
    Prépare l'image. Contrairement à EasyOCR, Paddle performe mieux 
    sans binarisation agressive (on évite le noir et blanc pur).
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    # A. Passage en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # B. CLAHE pour uniformiser les contrastes (ton idée originale, excellente)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # C. Upscaling : On agrandit pour que les petits caractères soient nets
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # D. Léger flou pour lisser le "bruit" numérique sans casser les bords
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    final_img  = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

    return final_img

def clean_ocr_text(text):
    """Nettoie et normalise le texte extrait."""
    t = text.upper().strip()
    # Remplacement des erreurs communes de ponctuation
    t = re.sub(r'[|I\\:;]', '/', t)
    # Correction spécifique au chiffre 0 et 7
    t = re.sub(r'(?<=\d)O(?=\d)', '0', t)
    t = re.sub(r'[?T]', '7', t)
    return t

def extract_text(image_path):
    """Fonction principale d'extraction."""
    img_ready = preprocess(image_path)
    if img_ready is None:
        return "Erreur de chargement"

    # L'OCR renvoie une liste de listes (boîtes, texte, confiance)
    result = ocr.ocr(img_ready)

    extracted_lines = []
    
    if result:
        for line in result:
            for word in line:
                text = word[1][0]
                confidence = word[1][1]
                if confidence > 0.45:
                    cleaned = clean_ocr_text(text)
                    extracted_lines.append(cleaned)

    full_text = " ".join(extracted_lines)
    return full_text

