import tkinter as tk
from tkinter import messagebox, filedialog
from generator import generer_codes_promo
from storage import sauvegarder_codes, charger_codes, modifier_statut_code
import pyperclip
from PIL import Image, ImageDraw, ImageFont
import os
from fpdf import FPDF

# Variable pour stocker l'image de fond
image_fond_path = None

# Fenêtre principale
root = tk.Tk()
root.title("Gestion des Codes Promo by inoussasakine@gmail.com")
root.geometry("600x650")

# Conteneur principal pour changer d'interface
contenu_frame = tk.Frame(root)
contenu_frame.pack(fill=tk.BOTH, expand=True)

### === MENU PRINCIPAL === ###
def afficher_menu():
    for widget in contenu_frame.winfo_children():
        widget.destroy()

    tk.Label(contenu_frame, text="Bienvenue dans l'application", font=("Arial", 16)).pack(pady=20)

    btn_generateur = tk.Button(contenu_frame, text="Générateur de Codes Promo", command=afficher_generateur, height=2)
    btn_generateur.pack(pady=10, fill=tk.X, padx=50)

    btn_manager = tk.Button(contenu_frame, text="Manager de Codes Promo", command=afficher_manager, height=2)
    btn_manager.pack(pady=10, fill=tk.X, padx=50)

### === GÉNÉRATEUR DE CODES PROMO === ###
def afficher_generateur():
    for widget in contenu_frame.winfo_children():
        widget.destroy()

    tk.Label(contenu_frame, text="Générateur de Codes Promo", font=("Arial", 14)).pack(pady=10)

    tk.Label(contenu_frame, text="Nombre de codes :").pack()
    entry_nombre = tk.Entry(contenu_frame)
    entry_nombre.pack()

    tk.Label(contenu_frame, text="Longueur des codes :").pack()
    entry_longueur = tk.Entry(contenu_frame)
    entry_longueur.pack()

    tk.Label(contenu_frame, text="Préfixe :").pack()
    entry_prefixe = tk.Entry(contenu_frame)
    entry_prefixe.insert(0, "PROMO")
    entry_prefixe.pack()

    liste_codes = tk.Listbox(contenu_frame, height=10)
    liste_codes.pack()

    def generer():
        try:
            nombre = int(entry_nombre.get())
            longueur = int(entry_longueur.get())
            prefixe = entry_prefixe.get()

            codes = generer_codes_promo(nombre, longueur, prefixe)
            sauvegarder_codes(codes)

            liste_codes.delete(0, tk.END)
            for code in codes:
                liste_codes.insert(tk.END, code)
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des nombres valides.")

    def choisir_image_fond():
        global image_fond_path
        image_fond_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if image_fond_path:
            messagebox.showinfo("Image chargée", "Image de fond sélectionnée.")

    def generer_une_image(code):
        """Génère une seule image pour un code donné"""
        if not image_fond_path:
            return

        try:
            img = Image.open(image_fond_path)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 40)

            img_width, img_height = img.size
            bbox = draw.textbbox((0, 0), code, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

            rect_padding = 20
            rect_x1 = (img_width - text_width - rect_padding) // 2
            rect_y1 = (img_height - text_height - rect_padding) // 2
            rect_x2 = rect_x1 + text_width + rect_padding
            rect_y2 = rect_y1 + text_height + rect_padding

            draw.rounded_rectangle([rect_x1, rect_y1, rect_x2, rect_y2], radius=15, fill="white")
            draw.text((rect_x1 + rect_padding // 2, rect_y1 + rect_padding // 2), code, font=font, fill="black")

            if not os.path.exists("images"):
                os.makedirs("images")
            img.save(f"images/{code}.png")
        except Exception as e:
            print(f"Erreur lors de la génération de l'image pour {code} : {e}")

    def generer_toutes_images():
        """Génère toutes les images en une seule fois"""
        if not image_fond_path:
            messagebox.showwarning("Erreur", "Veuillez sélectionner une image de fond d'abord.")
            return

        codes = liste_codes.get(0, tk.END)
        if not codes:
            messagebox.showwarning("Erreur", "Aucun code à générer en image.")
            return

        for code in codes:
            generer_une_image(code)

        messagebox.showinfo("Images Générées", "Toutes les images ont été créées avec succès.")

    btn_generer = tk.Button(contenu_frame, text="Générer", command=generer)
    btn_generer.pack(pady=5)

    btn_choisir_image = tk.Button(contenu_frame, text="Choisir Image Fond", command=choisir_image_fond)
    btn_choisir_image.pack(pady=5)

    btn_generer_images = tk.Button(contenu_frame, text="Générer toutes les images", command=generer_toutes_images)
    btn_generer_images.pack(pady=5)

    btn_export_pdf = tk.Button(contenu_frame, text="Exporter en PDF", command=exporter_pdf)
    btn_export_pdf.pack(pady=5)


    btn_retour = tk.Button(contenu_frame, text="Retour au menu", command=afficher_menu)
    btn_retour.pack(pady=10)

### === pdf === ###
def exporter_pdf():
    """Générer un PDF avec tous les codes promo générés"""
    codes = liste_codes.get(0, tk.END)
    if not codes:
        messagebox.showwarning("Erreur", "Aucun code généré.")
        return
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Liste des Codes Promo", ln=True, align='C')
    pdf.ln(10)

    for code in codes:
        pdf.cell(200, 10, txt=code, ln=True, align='L')

    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")
    pdf.output("pdfs/codes_promo.pdf")

    messagebox.showinfo("PDF Exporté", "Liste des codes enregistrée en PDF.")

# Ajout du bouton pour exporter en PDF
btn_export_pdf = tk.Button(contenu_frame, text="Exporter en PDF", command=exporter_pdf)
btn_export_pdf.pack(pady=5)



### === MANAGER DE CODES PROMO === ###
def afficher_manager():
    for widget in contenu_frame.winfo_children():
        widget.destroy()

    tk.Label(contenu_frame, text="Manager de Codes Promo", font=("Arial", 14)).pack(pady=10)

    entry_recherche = tk.Entry(contenu_frame)
    entry_recherche.pack()

    liste_codes = tk.Listbox(contenu_frame, height=15)
    liste_codes.pack(fill=tk.BOTH, expand=True)

    def rechercher():
        """Met à jour la liste des codes en fonction de la recherche"""
        terme = entry_recherche.get().strip().lower()
        liste_codes.delete(0, tk.END)

        for ligne in charger_codes():
            if len(ligne) == 2:
                code, statut = ligne
                if terme in code.lower():
                    liste_codes.insert(tk.END, f"{code} - {statut}")

    def changer_statut():
        """Change le statut d'un code promo sélectionné"""
        selection = liste_codes.curselection()
        if not selection:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un code.")
            return

        index = selection[0]
        code_selectionne = liste_codes.get(index).split(" - ")[0]

        codes = charger_codes()
        for i, (code, statut) in enumerate(codes):
            if code == code_selectionne:
                nouveau_statut = "Utilisé" if statut == "Libre" else "Libre"
                modifier_statut_code(code, nouveau_statut)
                rechercher()  # Rafraîchir la liste après modification
                return

    btn_rechercher = tk.Button(contenu_frame, text="Rechercher", command=rechercher)
    btn_rechercher.pack()

    btn_statut = tk.Button(contenu_frame, text="Changer Statut", command=changer_statut)
    btn_statut.pack()

    btn_retour = tk.Button(contenu_frame, text="Retour au menu", command=afficher_menu)
    btn_retour.pack(pady=10)

    rechercher()  # Charger la liste au démarrage

# Afficher le menu principal au démarrage
afficher_menu()

# Lancer l'application
root.mainloop()
