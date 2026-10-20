"""Lecture et écriture des fichiers de configuration JSON du dossier config/."""

import json
from pathlib import Path

# Racine du projet : le dossier qui contient visiocheck/, config/, data/...
RACINE = Path(__file__).resolve().parent.parent
DOSSIER_CONFIG = RACINE / "config"


def lire_json(nom_fichier):
    """Lit un fichier JSON de config/ et renvoie son contenu (dictionnaire)."""
    chemin = DOSSIER_CONFIG / nom_fichier
    with open(chemin, encoding="utf-8") as fichier:
        return json.load(fichier)


def ecrire_json(nom_fichier, donnees):
    """Écrit un dictionnaire dans un fichier JSON de config/, lisible par un humain."""
    chemin = DOSSIER_CONFIG / nom_fichier
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, indent=2, ensure_ascii=False)


def charger_zones():
    """Renvoie la liste des zones du gabarit."""
    return lire_json("gabarit.json")["zones"]


def charger_couleurs():
    """Renvoie le dictionnaire des couleurs et de leurs plages HSV."""
    return lire_json("couleurs.json")["couleurs"]


def charger_reglages():
    """Renvoie les réglages généraux (caméra, seuils, journal)."""
    return lire_json("reglages.json")


def chemin_projet(chemin_relatif):
    """Transforme un chemin relatif à la racine du projet en chemin absolu."""
    return RACINE / chemin_relatif


def verifier_gabarit(zones, couleurs, largeur_image, hauteur_image):
    """Vérifie que le gabarit est cohérent avec les couleurs connues et la taille de l'image.

    Renvoie la liste des problèmes trouvés, en phrases claires (liste vide si tout va bien).
    """
    if not zones:
        return ["Le gabarit ne contient aucune zone : lance scripts/calibrer_zones.py."]

    problemes = []
    for zone in zones:
        nom = zone["nom"]
        if zone["couleur_attendue"] not in couleurs:
            problemes.append(
                f"Zone {nom} : couleur attendue « {zone['couleur_attendue']} » inconnue "
                f"(couleurs possibles : {', '.join(couleurs)}).")
        if zone["largeur"] <= 0 or zone["hauteur"] <= 0:
            problemes.append(f"Zone {nom} : largeur et hauteur doivent être positives.")
        sort_de_l_image = (zone["x"] < 0 or zone["y"] < 0
                           or zone["x"] + zone["largeur"] > largeur_image
                           or zone["y"] + zone["hauteur"] > hauteur_image)
        if sort_de_l_image:
            problemes.append(
                f"Zone {nom} : sort de l'image ({largeur_image}x{hauteur_image}). "
                "La caméra a peut-être changé de résolution : recalibre avec scripts/calibrer_zones.py.")
    return problemes
