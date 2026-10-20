"""Journal CSV des contrôles et sauvegarde des photos NOK."""

import csv
from datetime import datetime
from pathlib import Path

import cv2

COLONNES = ["horodatage", "verdict_global", "zones_en_defaut", "detail"]

# Excel en français attend des « ; » entre les colonnes (la virgule y sert aux décimales).
SEPARATEUR_COLONNES = ";"
# À l'intérieur d'une colonne, on sépare les zones par des virgules : Z2,Z4
SEPARATEUR_ZONES = ","
# utf-8-sig ajoute une signature en début de fichier : Excel affiche alors bien les accents.
ENCODAGE = "utf-8-sig"


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
        # Ex. "Z2,Z4" : noms des zones en défaut.
        "zones_en_defaut": SEPARATEUR_ZONES.join(r["nom"] for r in defauts),
        # Ex. "Z2=MANQUANT,Z4=ERREUR(rouge)"
        "detail": SEPARATEUR_ZONES.join(_decrire_defaut(r) for r in defauts),
    }
    # newline="" : évite les lignes vides en trop dans le CSV sous Windows.
    with open(chemin_csv, "a", newline="", encoding=ENCODAGE) as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=COLONNES, delimiter=SEPARATEUR_COLONNES)
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
    ecrire_image(chemin, image)
    return chemin


def ecrire_image(chemin, image):
    """Enregistre une image ; lève une erreur claire si l'écriture échoue.

    cv2.imwrite ne plante pas en cas d'échec : il renvoie simplement False.
    Sans ce contrôle, une photo NOK pourrait ne jamais être enregistrée sans que personne
    ne le remarque (cas connu : chemin avec accents sous Windows, disque plein).
    """
    if not cv2.imwrite(str(chemin), image):
        raise RuntimeError(f"Impossible d'enregistrer l'image {chemin}.")


def lire_journal(chemin_csv):
    """Relit le journal CSV et renvoie la liste des lignes (dictionnaires)."""
    with open(chemin_csv, newline="", encoding=ENCODAGE) as fichier:
        lignes = list(csv.DictReader(fichier, delimiter=SEPARATEUR_COLONNES))
    if lignes and "verdict_global" not in lignes[0]:
        raise RuntimeError(
            f"{chemin_csv} n'est pas au format attendu (colonnes séparées par « ; »). "
            "Renomme ou supprime cet ancien journal.")
    return lignes


def calculer_synthese(lignes):
    """Calcule la synthèse d'un journal : volumes, taux, zones les plus en défaut, taux par heure.

    `lignes` est la liste renvoyée par lire_journal().
    """
    total = len(lignes)
    nb_ok = sum(1 for ligne in lignes if ligne["verdict_global"] == "OK")

    defauts_par_zone = {}
    par_heure = {}
    for ligne in lignes:
        for zone in filter(None, ligne["zones_en_defaut"].split(SEPARATEUR_ZONES)):
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
