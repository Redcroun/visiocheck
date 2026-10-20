"""Lire la couleur HSV d'un point en cliquant sur l'image (sert à calibrer config/couleurs.json).

Utilisation :
    python scripts/hsv_picker.py                          # webcam en direct
    python scripts/hsv_picker.py data/exemples/photo.png  # image fichier

Clic gauche : affiche la moyenne H, S, V d'un carré de 5x5 pixels autour du clic.
Touche q : quitter.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

from visiocheck import affichage, configuration
from visiocheck.camera import image_suivante, liberer, ouvrir_source

NOM_FENETRE = "VisioCheck - pipette HSV"
DEMI_COTE = 2  # carré de 5x5 pixels : 2 pixels de chaque côté du point cliqué

etat = {"image": None, "mesure": None}


def moyenne_hsv(image_bgr, x, y):
    """Renvoie la moyenne (H, S, V) d'un petit carré autour du point (x, y).

    Une moyenne sur plusieurs pixels est plus fiable qu'un pixel seul,
    qui peut être faussé par le bruit du capteur.
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    carre = hsv[max(y - DEMI_COTE, 0):y + DEMI_COTE + 1, max(x - DEMI_COTE, 0):x + DEMI_COTE + 1]
    h, s, v = carre.reshape(-1, 3).mean(axis=0)
    return int(h), int(s), int(v)


def gerer_souris(evenement, x, y, drapeaux, parametre):
    """Au clic gauche, mesure la couleur HSV autour du point cliqué."""
    if evenement == cv2.EVENT_LBUTTONDOWN and etat["image"] is not None:
        h, s, v = moyenne_hsv(etat["image"], x, y)
        etat["mesure"] = (x, y, h, s, v)
        print(f"Point ({x}, {y}) -> H={h}  S={s}  V={v}")


def main():
    reglages = configuration.charger_reglages()
    image_fichier, camera = ouvrir_source(sys.argv[1:], reglages["camera"])

    cv2.namedWindow(NOM_FENETRE)
    cv2.setMouseCallback(NOM_FENETRE, gerer_souris)
    print("Clique sur une pièce pour lire sa couleur HSV. q = quitter.")
    print("Rappel : dans OpenCV, H va de 0 à 179 (et non 0 à 360), S et V de 0 à 255.")

    while True:
        etat["image"] = image_suivante(image_fichier, camera)
        ecran = etat["image"].copy()
        if etat["mesure"] is not None:
            x, y, h, s, v = etat["mesure"]
            cv2.circle(ecran, (x, y), 6, affichage.BLANC, 2)
            affichage.ecrire(ecran, f"H={h}  S={s}  V={v}", (10, 25))
        cv2.imshow(NOM_FENETRE, ecran)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    liberer(camera)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as erreur:
        print(f"Erreur : {erreur}")
        sys.exit(1)
