"""Crée des images de démonstration (gabarit virtuel) dans data/exemples/.

Permet d'essayer VisioCheck sans webcam ni pièces :
    python scripts/creer_images_demo.py
    python scripts/main.py data/exemples/demo_ok.png
    python scripts/main.py data/exemples/demo_nok.png
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np

from visiocheck import configuration
from visiocheck.journal import ecrire_image

# Couleurs « pures » en BGR pour dessiner les pièces virtuelles.
COULEURS_BGR = {
    "rouge": (0, 0, 220),
    "jaune": (0, 220, 230),
    "vert": (0, 170, 0),
    "bleu": (200, 60, 0),
}


def dessiner_gabarit(zones, pieces, largeur=640, hauteur=480):
    """Dessine un fond blanc et une pièce colorée dans chaque zone.

    `pieces` associe un nom de zone à une couleur, ou à None pour un emplacement vide.
    """
    image = np.full((hauteur, largeur, 3), 235, dtype=np.uint8)  # fond gris très clair
    for zone in zones:
        couleur = pieces.get(zone["nom"])
        if couleur is None:
            continue
        marge = 15  # la pièce est un peu plus petite que la zone
        coin1 = (zone["x"] + marge, zone["y"] + marge)
        coin2 = (zone["x"] + zone["largeur"] - marge, zone["y"] + zone["hauteur"] - marge)
        cv2.rectangle(image, coin1, coin2, COULEURS_BGR[couleur], -1)
    return image


def main():
    zones = configuration.charger_zones()
    dossier = configuration.chemin_projet("data/exemples")
    dossier.mkdir(parents=True, exist_ok=True)

    tout_bon = {z["nom"]: z["couleur_attendue"] for z in zones}
    # NOK : 2e zone vide, dernière zone avec une pièce rouge à la place de l'attendue.
    defauts = dict(tout_bon)
    defauts[zones[1]["nom"]] = None
    if zones[-1]["couleur_attendue"] != "rouge":
        defauts[zones[-1]["nom"]] = "rouge"
    else:
        defauts[zones[-1]["nom"]] = "bleu"

    ecrire_image(dossier / "demo_ok.png", dessiner_gabarit(zones, tout_bon))
    ecrire_image(dossier / "demo_nok.png", dessiner_gabarit(zones, defauts))
    print(f"Images créées dans {dossier} : demo_ok.png et demo_nok.png")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as erreur:
        print(f"Erreur : {erreur}")
        sys.exit(1)
