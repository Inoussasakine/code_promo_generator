import tkinter as tk
from tkinter import filedialog, messagebox
from generator import generer_codes_promo
from storage import sauvegarder_codes, charger_codes
import pyperclip
from PIL import Image, ImageDraw, ImageFont
import os
from fpdf import FPDF

# Variable globale pour stocker l'image de fond
image_fond_path = None

def copier_code():
    selection = liste_codes.curselection()
    if selection:
        code = liste_codes.get(selection[0])
        pyperclip.copy(code)
        messagebox.showinfo("Copié !", f"Le code '{code}' a été copié dans le presse-papier.")
    else:
        messagebox.showwarning("Erreur", "Veuillez sélectionner un code à copier.")

def choisir_image_fond():
    global image_fond_path
    image_fond_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
    if image_fond_path:
        messagebox.showinfo("Image chargée", "L'image de fond a été sélectionnée avec succès.")

def generer_image():
    selection = liste_codes.curselection()
    if selection:
        code = liste_codes.get(selection[0])

        if not image_fond_path:
            messagebox.showwarning("Erreur", "Veuillez d'abord sélectionner une image de fond.")
            return

        try:
            img = Image.open(image_fond_path)
            draw = ImageDraw.Draw(img)

            # Charger la police (Arial ou police par défaut)
            try:
                font = ImageFont.truetype("arial.ttf", 40)  # Arial taille 40
            except IOError:
                font = ImageFont.load_default()

            # Obtenir la taille de l'image
            img_width, img_height = img.size

            # Obtenir la taille du texte avec textbbox()
            bbox = draw.textbbox((0, 0), code, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Déterminer la position du rectangle
            rect_padding = 20  # Marge autour du texte
            rect_x1 = (img_width - text_width - rect_padding) // 2
            rect_y1 = (img_height - text_height - rect_padding) // 2
            rect_x2 = rect_x1 + text_width + rect_padding
            rect_y2 = rect_y1 + text_height + rect_padding

            # Dessiner un rectangle arrondi blanc
            draw.rounded_rectangle([rect_x1, rect_y1, rect_x2, rect_y2], radius=15, fill="white")

            # Positionner le texte centré
            text_x = (img_width - text_width) // 2
            text_y = (img_height - text_height) // 2
            draw.text((text_x, text_y), code, font=font, fill="black")

            # Sauvegarde de l'image
            if not os.path.exists("images"):
                os.makedirs("images")
            img_path = f"images/{code}.png"
            img.save(img_path)

            messagebox.showinfo("Image générée", f"L'image du code '{code}' a été enregistrée dans {img_path}.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer l'image : {e}")
    else:
        messagebox.showwarning("Erreur", "Veuillez sélectionner un code.")

def generer_pdf():
    codes = liste_codes.get(0, tk.END)

    if not codes:
        messagebox.showwarning("Erreur", "Aucun code à enregistrer.")
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Liste des Codes Promo", ln=True, align='C')
    pdf.ln(10)

    for code in codes:
        pdf.cell(200, 10, txt=code, ln=True, align='L')

    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")
    pdf_path = "pdfs/codes_promo.pdf"
    pdf.output(pdf_path)

    messagebox.showinfo("PDF généré", f"Le fichier PDF a été enregistré dans {pdf_path}.")

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

# Fenêtre principale
root = tk.Tk()
root.title("Générateur de Codes Promo")
root.geometry("500x550")

# Entrées utilisateur
tk.Label(root, text="Nombre de codes :").pack()
entry_nombre = tk.Entry(root)
entry_nombre.pack()

tk.Label(root, text="Longueur des codes :").pack()
entry_longueur = tk.Entry(root)
entry_longueur.pack()

tk.Label(root, text="Préfixe :").pack()
entry_prefixe = tk.Entry(root)
entry_prefixe.insert(0, "PROMO")
entry_prefixe.pack()

# Bouton de génération
btn_generer = tk.Button(root, text="Générer", command=generer)
btn_generer.pack()

# Liste des codes générés
liste_codes = tk.Listbox(root, height=10)
liste_codes.pack()

# Charger les anciens codes
for code in charger_codes():
    liste_codes.insert(tk.END, code)

# Bouton pour copier un code promo
btn_copier = tk.Button(root, text="Copier le code sélectionné", command=copier_code)
btn_copier.pack()

# Bouton pour sélectionner une image de fond
btn_image_fond = tk.Button(root, text="Choisir une image de fond", command=choisir_image_fond)
btn_image_fond.pack()

# Bouton pour générer une image du code promo
btn_image = tk.Button(root, text="Générer une image avec le code", command=generer_image)
btn_image.pack()

# Bouton pour générer un PDF avec tous les codes
btn_pdf = tk.Button(root, text="Exporter en PDF", command=generer_pdf)
btn_pdf.pack()

# Démarrer l'application
root.mainloop()
