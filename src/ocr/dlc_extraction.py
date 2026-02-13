import re
from datetime import datetime, date 
from src.ocr.txt_extraction import MONTHS

def extract_dlc(text):
    if not text:
        return None
        
    text_upper = text.upper()
    found_dates = []

    # --- 1. PATTERNS AMÉLIORÉS ---
    
    # Pattern 1 : JJ/MM/AAAA ou JJ/MM/AA
    pattern_full = r"\b(\d{1,2})\s*[\/\-\.\s]\s*(\d{1,2})\s*[\/\-\.\s]\s*(\d{2,4})\b"
    
    # Pattern 2 : MM/AAAA (Sans le jour, fréquent sur conserves/cosmétiques)
    pattern_short = r"\b(\d{1,2})\s*[\/\-\.]\s*(\d{4})\b"
    
    # Pattern 3 : Texte (12 JAN 2026)
    pattern_text = r"\b(\d{1,2})\s*(" + "|".join(MONTHS.keys()) + r")\s*(\d{2,4})\b"

    # Extraction Numérique Complète
    for match in re.finditer(pattern_full, text_upper):
        d, m, y = match.groups()
        if len(y) == 2: y = "20" + y
        try:
            found_dates.append(date(int(y), int(m), int(d)))
        except ValueError: continue

    # Extraction Numérique Courte (On fixe le jour au 1er du mois par défaut ou dernier)
    for match in re.finditer(pattern_short, text_upper):
        m, y = match.groups()
        try:
            # Pour une DLC, si on a juste MM/YYYY, on considère souvent la fin du mois
            # Mais par sécurité, on peut mettre le 1er.
            found_dates.append(date(int(y), int(m), 1))
        except ValueError: continue

    # Extraction Texte
    for match in re.finditer(pattern_text, text_upper):
        d, m_name, y = match.groups()
        if len(y) == 2: y = "20" + y
        try:
            found_dates.append(date(int(y), int(MONTHS[m_name]), int(d)))
        except ValueError: continue

    if not found_dates:
        return None

    # --- 2. FILTRAGE INTELLIGENT ---
    
    current_year = date.today().year
    # On élargit un peu : de l'année dernière à dans 10 ans
    valid_dates = [d for d in found_dates if current_year - 1 <= d.year <= current_year + 10]
    
    if not valid_dates:
        return None

    # Si on a un mot clé d'expiration (E, EXP, AVANT) juste avant une date
    # On priorise cette date plutôt que de prendre le simple Max.
    keywords_dlc = [
    # Français
    "EXP", "DLC", "DLUO", "DDM", "AVANT", "CONSOMMER", "CONSO", "JUSQU", "FIN",
    # Anglais
    "BEST", "BEFORE", "BBD", "BB", "USE", "BY", "EXPIRY", "EXPIRES", "END",
    # Codes courts techniques
    "E:", "ED:", "EXP.", "V:", "VAL:" 
    ]
    
    for d in valid_dates:
        d_str = d.strftime("%d")
        # On regarde les 15 caractères avant la date trouvée
        pos = text_upper.find(d_str)
        context = text_upper[max(0, pos-15):pos]
        if any(kw in context for kw in keywords_dlc):
            return d

    # Par défaut, la date la plus lointaine (évite la date de production)
    return max(valid_dates)
