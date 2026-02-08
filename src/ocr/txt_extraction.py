import cv2
import easyocr

# Mois anglais + français
MONTHS = {
    "JAN":1, "JANV":1, "FEB":2, "FEV":2, "FÉV":2, "MAR":3, "MARS":3,
    "APR":4, "AVR":4, "MAY":5, "MAI":5, "JUN":6, "JUI":7, "JUL":7, "JUIL":7,
    "AUG":8, "AOU":8, "AOÛ":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12, "DÉC":12
}

# Initialisation EasyOCR (UNE FOIS)
reader = easyocr.Reader(['fr','en'], gpu=False)

def extract_text(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image introuvable : {image_path}")
    
    # Prétraitement simple pour améliorer le contraste
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Lecture (sans paragraph=True pour garder la précision des lignes)
    result = reader.readtext(gray)
    
    # Correction : On récupère TOUT le texte avant de retourner
    extracted_lines = []
    for _, text, _ in result:
        # Nettoyage des erreurs OCR fréquentes sur les dates
        clean_text = text.upper().replace('I', '1').replace('|', '/').replace('O', '0')
        extracted_lines.append(clean_text)
    
    full_text = "\n".join(extracted_lines)
    print(f"--- Texte Extrait ---\n{full_text}\n-------------------")
    return full_text