import random
import string

def generer_code_promo(longueur=10, prefixe="PROMO"):
    caracteres = string.ascii_uppercase + string.digits  # Lettres majuscules et chiffres
    code_aleatoire = ''.join(random.choices(caracteres, k=longueur))
    return f"{prefixe}{code_aleatoire}"

def generer_codes_promo(nombre=10, longueur=10, prefixe="PROMO"):
    return [generer_code_promo(longueur, prefixe) for _ in range(nombre)]
