import csv
import os

FICHIER_CSV = "codes_promo.csv"

def sauvegarder_codes(codes):
    """Sauvegarde les codes promo avec le statut 'Libre' par défaut."""
    with open(FICHIER_CSV, "a", newline="") as fichier:
        writer = csv.writer(fichier)
        for code in codes:
            writer.writerow([code, "Libre"])

def charger_codes():
    """Charge les codes promo depuis le fichier CSV, en s'assurant d'avoir deux valeurs par ligne."""
    if not os.path.exists(FICHIER_CSV):
        return []

    codes = []
    with open(FICHIER_CSV, "r") as fichier:
        reader = csv.reader(fichier)
        for row in reader:
            if len(row) == 2:  # Vérifier que chaque ligne contient bien un code + statut
                codes.append(row)
            elif len(row) == 1:  # Si une ligne ne contient qu'un code, ajouter le statut manquant
                codes.append([row[0], "Libre"])
    
    return codes

def modifier_statut_code(code, nouveau_statut):
    """Modifie le statut d’un code promo."""
    codes = charger_codes()
    for i, row in enumerate(codes):
        if row[0] == code:
            codes[i][1] = nouveau_statut  # Changer le statut

    # Réécrire le fichier CSV avec les nouveaux statuts
    with open(FICHIER_CSV, "w", newline="") as fichier:
        writer = csv.writer(fichier)
        writer.writerows(codes)
