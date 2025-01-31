import tkinter as tk
from tkinter import messagebox, filedialog
from generator import generer_codes_promo
from storage import sauvegarder_codes, charger_codes, modifier_statut_code
import pyperclip
from PIL import Image, ImageDraw, ImageFont
import os
from fpdf import FPDF
from datetime import datetime

# Variable pour stocker l'image de fond
image_fond_path = None
# 📌 Met le chemin du logo ici
LOGO_PATH = "logo.png"  # Assure-toi que l'image est bien dans le dossier du projet

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
    global liste_codes  # Rendre liste_codes accessible à toute la fenêtre
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
            font = ImageFont.truetype("arialbd.ttf", 60) #Modifier la taille du texte code sur image VRAI

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

    # Ajout bouton pour exporter images en pdf
    btn_export_images_pdf = tk.Button(contenu_frame, text="Exporter Images en PDF", command=exporter_images_pdf)
    btn_export_images_pdf.pack(pady=5)

    btn_retour = tk.Button(contenu_frame, text="Retour au menu", command=afficher_menu)
    btn_retour.pack(pady=10)



### === pdf === ###
def exporter_pdf():
    """Génère un PDF avec un tableau contenant les codes promo, numérotation, bénéficiaire et date"""
    global liste_codes  # Récupérer la variable globale

    try:
        codes = liste_codes.get(0, tk.END)  # Récupérer tous les codes
        # 📌 Récupérer la date actuelle
        date_aujourd_hui = datetime.today().strftime("%d/%m/%Y")

        if not codes:
            messagebox.showwarning("Erreur", "Aucun code à exporter.")
            return

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # 📌 Ajouter le logo (si le fichier existe)
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=10, y=5, w=30)  # Position (x, y) et largeur (w

        # 📌 Titre du document
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, f"Liste des Codes Promo du {date_aujourd_hui}", ln=True, align='C')
        pdf.ln(10)

        # 📌 Définition du tableau
        pdf.set_font("Arial", "B", 12)
        pdf.cell(10, 10, "N°", border=1, align="C")  # Numérotation
        pdf.cell(70, 10, "Code Promo", border=1, align="C")  # Code
        pdf.cell(70, 10, "Bénéficiaire", border=1, align="C")  # Bénéficiaire
        pdf.cell(40, 10, "Date", border=1, align="C")  # Date
        pdf.ln()

        # 📌 Remplir le tableau avec les données
        pdf.set_font("Arial", size=11)

        for i, code in enumerate(codes, start=1):
            pdf.cell(10, 10, str(i), border=1, align="C")  # Numérotation
            pdf.cell(70, 10, code, border=1, align="C")  # Code promo
            pdf.cell(70, 10, "", border=1, align="C")  # Bénéficiaire par défaut
            pdf.cell(40, 10, "", border=1, align="C")  # Date actuelle
            pdf.ln()

        # 📌 Créer le dossier "pdfs" s'il n'existe pas
        if not os.path.exists("pdfs"):
            os.makedirs("pdfs")

        pdf_path = "pdfs/codes_promo.pdf"
        pdf.output(pdf_path)

        messagebox.showinfo("PDF Exporté", f"Liste des codes enregistrée en PDF :\n{pdf_path}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'exporter en PDF : {e}")

# === Exporter images pdf ===
def exporter_images_pdf():
    """Génère un PDF contenant 4 images des codes promo par page avec un redimensionnement proportionnel"""
    global liste_codes  # Récupérer la variable globale

    try:
        codes = liste_codes.get(0, tk.END)  # Récupérer tous les codes

        if not codes:
            messagebox.showwarning("Erreur", "Aucune image à exporter.")
            return

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()

        # 📌 Récupérer la date actuelle
        date_aujourd_hui = datetime.today().strftime("%d/%m/%Y")

        # 📌 Ajouter le titre avec la date du jour
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, f"Images des Codes Promo du {date_aujourd_hui}", ln=True, align='C')
        pdf.ln(10)

        # 📌 Position et taille des images
        x_start = 15
        y_start = 40
        page_width = 210  # Largeur totale A4 en mm
        page_height = 297  # Hauteur totale A4 en mm
        max_width = 85  # Largeur max d'une image (ajusté pour 2 images par ligne)
        max_height = 85  # Hauteur max d'une image (ajusté pour 2 lignes)

        images_per_row = 2  # 2 images par ligne
        images_per_page = 4  # 4 images par page (2 lignes de 2 images)

        count = 0
        img_found = False

        for code in codes:
            img_path = f"images/{code}.png"
            if os.path.exists(img_path):
                # 📌 Redimensionner l'image proportionnellement
                with Image.open(img_path) as img:
                    img_w, img_h = img.size
                    ratio = min(max_width / img_w, max_height / img_h)
                    new_w = int(img_w * ratio)
                    new_h = int(img_h * ratio)

                row = count // images_per_row  # Ligne actuelle (0 ou 1)
                col = count % images_per_row  # Colonne actuelle (0 ou 1)

                x = x_start + (col * (max_width + 10))  # Position X
                y = y_start + (row * (max_height + 10))  # Position Y

                pdf.image(img_path, x=x, y=y, w=new_w, h=new_h)

                count += 1
                img_found = True

                if count >= images_per_page:  # Si 4 images sont placées, passer à la page suivante
                    pdf.add_page()
                    count = 0  # Réinitialiser le compteur pour la nouvelle page
                    y_start = 40  # Réinitialiser la position Y

            else:
                print(f"Image non trouvée pour : {code}")

        if not img_found:
            messagebox.showwarning("Erreur", "Aucune image trouvée pour les codes générés.")
            return

        # 📌 Créer le dossier "pdfs" s'il n'existe pas
        if not os.path.exists("pdfs"):
            os.makedirs("pdfs")

        pdf_path = f"pdfs/images_codes_promo_{date_aujourd_hui.replace('/', '-')}.pdf"
        pdf.output(pdf_path)

        messagebox.showinfo("PDF Exporté", f"PDF contenant les images enregistré :\n{pdf_path}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'exporter les images en PDF : {e}")
        
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
