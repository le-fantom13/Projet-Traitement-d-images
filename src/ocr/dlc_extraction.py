import re
from datetime import datetime, date 
from .txt_extraction import MONTHS

def extract_dlc(text):
    if not text:
        return None
        
    text_upper = text.upper()
    found_dates = []

    # --- 1. COLLECTE DE TOUTES LES DATES POSSIBLES ---
    
    # Pattern Numérique flexible (JJ/MM/AA ou JJ/MM/AAAA)
    # On accepte / - . ou espace comme séparateur
    pattern_numeric = r"\b(\d{1,2})[\/\-\.\s](\d{1,2})[\/\-\.\s](\d{2,4})\b"
    
    # Pattern Mois en lettres (12 JAN 2026)
    pattern_text = r"\b(\d{1,2})\s*(" + "|".join(MONTHS.keys()) + r")\s*(\d{2,4})\b"

    # Extraction numérique
    for match in re.finditer(pattern_numeric, text_upper):
        d, m, y = match.groups()
        if len(y) == 2: y = "20" + y
        try:
            found_dates.append(date(int(y), int(m), int(d)))
        except ValueError: continue

    # Extraction texte
    for match in re.finditer(pattern_text, text_upper):
        d, m_name, y = match.groups()
        if len(y) == 2: y = "20" + y
        try:
            found_dates.append(date(int(y), MONTHS[m_name], int(d)))
        except ValueError: continue

    if not found_dates:
        return None

    # --- 2. LOGIQUE DE SÉLECTION (LE CERVEAU) ---
    
    # On élimine les dates aberrantes (ex: une année lue comme 2004 ou 2080)
    current_year = date.today().year
    valid_dates = [d for d in found_dates if current_year - 1 <= d.year <= current_year + 10]
    
    if not valid_dates:
        return None

    # STRATÉGIE ANTI-FABRICATION : 
    # Si on a plusieurs dates, la DLC est presque toujours la plus lointaine.
    # On cherche aussi si un mot-clé "EXP" ou "AVANT" est proche d'une des dates.
    
    keywords_dlc = ["EXP", "DLC", "AVANT", "BEST", "BEFORE", "CONSUMER"]
    
    # On vérifie si une des dates est précédée d'un mot-clé DLC dans le texte
    for d in valid_dates:
        date_str_short = d.strftime("%d") # On cherche juste le jour pour localiser
        if any(kw in text_upper.split(date_str_short)[0][-20:] for kw in keywords_dlc):
            return d # Si on trouve "EXP" juste avant, c'est gagné

    # Par défaut, on retourne la date la plus lointaine
    return max(valid_dates)