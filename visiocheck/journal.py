"""Journal CSV des contrôles et sauvegarde des photos NOK."""

import csv
from datetime import datetime
from pathlib import Path

import cv2

COLONNES = ["horodatage", "verdict_global", "zones_en_defaut", "detail"]


def maintenant():
    """Horodatage lisible et triable, ex. 2026-10-19 14:42:05."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def enregistrer_controle(chemin_csv, resultat, horodatage):
    """Ajoute une ligne au journal CSV (crée le fichier et son en-tête si besoin)."""
    chemin_csv = Path(chemin_csv)
    chemin_csv.parent.mkdir(parents=True, exist_ok=True)
    nouveau_fichier = not chemin_csv.exists()

    defauts = [r for r in resultat["zones"] if r["verdict"] != "OK"]
    ligne = {
        "horodatage": horodatage,
        "verdict_global": resultat["verdict_global"],
        # Ex. "Z2;Z4" : noms des zones en défaut séparés par des points-virgules.
        "zones_en_defaut": ";".join(r["nom"] for r in defauts),
        # Ex. "Z2=MANQUANT;Z4=ERREUR(rouge)"
        "detail": ";".join(_decrire_defaut(r) for r in defauts),
    }
    # newline="" : évite les lignes vides en trop dans le CSV sous Windows.
    with open(chemin_csv, "a", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=COLONNES, delimiter=",")
        if nouveau_fichier:
            ecrivain.writeheader()
        ecrivain.writerow(ligne)


def _decrire_defaut(resultat_zone):
    """Texte court décrivant le défaut d'une zone."""
    if resultat_zone["verdict"] == "ERREUR":
        return f'{resultat_zone["nom"]}=ERREUR({resultat_zone["couleur_detectee"]})'
    return f'{resultat_zone["nom"]}={resultat_zone["verdict"]}'


def sauvegarder_photo_nok(dossier, image, horodatage):
    """Enregistre la photo annotée d'un NOK ; renvoie le chemin du fichier."""
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    # Les « : » sont interdits dans les noms de fichiers Windows.
    base = "nok_" + horodatage.replace(":", "-").replace(" ", "_")
    chemin = dossier / f"{base}.jpg"
    numero = 2
    while chemin.exists():  # deux NOK dans la même seconde : on ajoute _2, _3...
        chemin = dossier / f"{base}_{numero}.jpg"
        numero += 1
    cv2.imwrite(str(chemin), image)
    return chemin


def lire_journal(chemin_csv):
    """Relit le journal CSV et renvoie la liste des lignes (dictionnaires)."""
    with open(chemin_csv, newline="", encoding="utf-8") as fichier:
        return list(csv.DictReader(fichier))


def calculer_synthese(lignes):
    """Calcule la synthèse d'un journal : volumes, taux, zones les plus en défaut, taux par heure.

    `lignes` est la liste renvoyée par lire_journal().
    """
    total = len(lignes)
    nb_ok = sum(1 for ligne in lignes if ligne["verdict_global"] == "OK")

    defauts_par_zone = {}
    par_heure = {}
    for ligne in lignes:
        for zone in filter(None, ligne["zones_en_defaut"].split(";")):
            defauts_par_zone[zone] = defauts_par_zone.get(zone, 0) + 1
        heure = ligne["horodatage"][11:13] + "h"  # "2026-10-19 14:42:05" -> "14h"
        compte = par_heure.setdefault(heure, {"total": 0, "OK": 0})
        compte["total"] += 1
        if ligne["verdict_global"] == "OK":
            compte["OK"] += 1

    # Tri du plus grand nombre de défauts au plus petit.
    top_zones = sorted(defauts_par_zone.items(), key=lambda paire: paire[1], reverse=True)
    return {
        "total": total,
        "ok": nb_ok,
        "nok": total - nb_ok,
        "taux_conformite": 100 * nb_ok / total if total else 0.0,
        "top_zones": top_zones,
        "par_heure": dict(sorted(par_heure.items())),
    }
