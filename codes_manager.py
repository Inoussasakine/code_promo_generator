import tkinter as tk
from tkinter import messagebox
from storage import charger_codes, modifier_statut_code

def rechercher_code():
    """Filtrer les codes promo affichés selon la recherche."""
    recherche = entry_recherche.get().strip().lower()
    liste_codes.delete(0, tk.END)
    
    for code, statut in charger_codes():
        if recherche in code.lower():
            liste_codes.insert(tk.END, f"{code} - {statut}")

def changer_statut():
    """Changer le statut d’un code promo sélectionné."""
    selection = liste_codes.curselection()
    if not selection:
        messagebox.showwarning("Erreur", "Veuillez sélectionner un code.")
        return
    
    code_selectionne = liste_codes.get(selection[0]).split(" - ")[0]
    
    codes = charger_codes()
    for code, statut in codes:
        if code == code_selectionne:
            nouveau_statut = "Utilisé" if statut == "Libre" else "Libre"
            modifier_statut_code(code, nouveau_statut)
            rechercher_code()  # Rafraîchir la liste
            return

# Fenêtre principale
root_manager = tk.Tk()
root_manager.title("Gestion des Codes Promo")
root_manager.geometry("400x500")

# Barre de recherche
tk.Label(root_manager, text="Rechercher un code :").pack()
entry_recherche = tk.Entry(root_manager)
entry_recherche.pack()

btn_rechercher = tk.Button(root_manager, text="Rechercher", command=rechercher_code)
btn_rechercher.pack()

# Liste des codes
liste_codes = tk.Listbox(root_manager, height=15)
liste_codes.pack()

# Bouton pour changer le statut
btn_statut = tk.Button(root_manager, text="Changer le statut", command=changer_statut)
btn_statut.pack()

# Charger tous les codes au démarrage
rechercher_code()

# Lancer l'interface
root_manager.mainloop()
