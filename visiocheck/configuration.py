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
