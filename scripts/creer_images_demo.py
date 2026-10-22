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
from visiocheck.affichage import coins
from visiocheck.journal import ecrire_image

# Couleurs « pures » en BGR pour dessiner les pièces virtuelles.
COULEURS_BGR = {
    "rouge": (0, 0, 220),
    "jaune": (0, 220, 230),
    "vert": (0, 170, 0),
    "bleu": (200, 60, 0),
}


# Écarts en pixels autour d'une zone, comme sur le gabarit imprimé (docs/) :
# le Post-it (76 mm) déborde un peu de la zone (70 mm), le cadre noir (85 mm) l'entoure.
DEBORD_PIECE = 6
DEBORD_CADRE = 16


def dessiner_gabarit(zones, pieces, largeur=640, hauteur=480):
    """Dessine le gabarit (feuille blanche, cadres noirs, noms des zones) et les pièces posées.

    `pieces` associe un nom de zone à une couleur, ou à None pour un emplacement vide.
    """
    image = np.full((hauteur, largeur, 3), 245, dtype=np.uint8)  # feuille blanche
    for zone in zones:
        coin1, coin2 = coins(zone, DEBORD_CADRE)
        cv2.rectangle(image, coin1, coin2, (0, 0, 0), 2)
        cv2.putText(image, zone["nom"], (coin1[0] + 2, coin1[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        couleur = pieces.get(zone["nom"])
        if couleur is not None:
            coin1, coin2 = coins(zone, DEBORD_PIECE)
            cv2.rectangle(image, coin1, coin2, COULEURS_BGR[couleur], -1)
    return image


def main():
    zones = configuration.charger_zones()
    dossier = configuration.chemin_projet("data/exemples")
    dossier.mkdir(parents=True, exist_ok=True)

    if len(zones) < 2:
        raise RuntimeError("Il faut au moins 2 zones dans config/gabarit.json pour créer la démo.")

    tout_bon = {z["nom"]: z["couleur_attendue"] for z in zones}
    # NOK : 2e zone vide (MANQUANT) ; dernière zone avec la pièce de la 1re zone,
    # comme une erreur de montage (ERREUR).
    defauts = dict(tout_bon)
    defauts[zones[1]["nom"]] = None
    defauts[zones[-1]["nom"]] = zones[0]["couleur_attendue"]

    ecrire_image(dossier / "demo_ok.png", dessiner_gabarit(zones, tout_bon))
    ecrire_image(dossier / "demo_nok.png", dessiner_gabarit(zones, defauts))
    print(f"Images créées dans {dossier} : demo_ok.png et demo_nok.png")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as erreur:
        print(f"Erreur : {erreur}")
        sys.exit(1)
