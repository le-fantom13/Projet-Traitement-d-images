from datetime import date

# Statut DLC
def check_expiry_status(expiry_date):
    if expiry_date is None:
        return "date inconnue"

    today = date.today()
    dif_jours =  (expiry_date - today).days


    if dif_jours > 3:
        return "Valide"
    elif 0 <= dif_jours <= 3:
        return "Alerte Gaspillage"
    else:
        return "Périmé"