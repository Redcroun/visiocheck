"""Dessiner les zones du gabarit à la souris et les enregistrer dans config/gabarit.json.

Utilisation :
    python scripts/calibrer_zones.py                         # avec la webcam
    python scripts/calibrer_zones.py data/exemples/photo.png # sur une image fichier

Déroulé :
    1. (webcam) espace = figer l'image
    2. cliquer-glisser pour dessiner une zone
    3. taper la 1re lettre de la couleur attendue (r = rouge, j = jaune, v = vert, b = bleu)
    4. z = annuler la dernière zone, e = enregistrer, q = quitter sans enregistrer
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

from visiocheck import affichage, configuration
from visiocheck.camera import lire_image, liberer, ouvrir_source

NOM_FENETRE = "VisioCheck - calibrage des zones"

# État partagé avec la fonction de la souris (comme des variables globales d'un script JS).
etat = {"debut": None, "courant": None, "rectangle_en_attente": None}


def gerer_souris(evenement, x, y, drapeaux, parametre):
    """Appelée par OpenCV à chaque mouvement ou clic de souris dans la fenêtre."""
    if evenement == cv2.EVENT_LBUTTONDOWN:
        etat["debut"] = (x, y)
        etat["courant"] = (x, y)
    elif evenement == cv2.EVENT_MOUSEMOVE and etat["debut"] is not None:
        etat["courant"] = (x, y)
    elif evenement == cv2.EVENT_LBUTTONUP and etat["debut"] is not None:
        (x1, y1), (x2, y2) = etat["debut"], (x, y)
        etat["debut"] = None
        # On range les coins pour que (x, y) soit toujours le coin haut-gauche.
        largeur, hauteur = abs(x2 - x1), abs(y2 - y1)
        if largeur > 10 and hauteur > 10:  # ignore les clics accidentels
            etat["rectangle_en_attente"] = (min(x1, x2), min(y1, y2), largeur, hauteur)


def obtenir_image_de_reference():
    """Renvoie l'image sur laquelle on dessine : fichier en argument, ou webcam figée."""
    reglages = configuration.charger_reglages()
    image_fichier, camera = ouvrir_source(sys.argv[1:], reglages["camera"])
    if image_fichier is not None:
        return image_fichier

    print("Place le gabarit sous la caméra, puis appuie sur espace pour figer l'image.")
    while True:
        image = lire_image(camera)
        apercu = image.copy()
        affichage.ecrire(apercu, "espace : figer l'image", (10, 25))
        cv2.imshow(NOM_FENETRE, apercu)
        if cv2.waitKey(30) & 0xFF == ord(" "):
            liberer(camera)
            return image


def main():
    couleurs = configuration.charger_couleurs()
    # Raccourcis clavier : 1re lettre de chaque couleur (r -> rouge, j -> jaune...).
    raccourcis = {ord(nom[0]): nom for nom in couleurs}
    texte_couleurs = "  ".join(f"{nom[0]}={nom}" for nom in couleurs)

    image = obtenir_image_de_reference()
    zones = []
    cv2.namedWindow(NOM_FENETRE)
    cv2.setMouseCallback(NOM_FENETRE, gerer_souris)
    print("Dessine les zones à la souris. " + texte_couleurs + "  z=annuler  e=enregistrer  q=quitter")

    while True:
        ecran = affichage.dessiner_zones(image, zones)
        if etat["debut"] is not None:  # rectangle en cours de dessin
            cv2.rectangle(ecran, etat["debut"], etat["courant"], affichage.BLANC, 1)
        if etat["rectangle_en_attente"] is not None:
            x, y, l, h = etat["rectangle_en_attente"]
            cv2.rectangle(ecran, (x, y), (x + l, y + h), affichage.BLANC, 2)
            affichage.ecrire(ecran, "Couleur attendue ? " + texte_couleurs, (10, 25))
        else:
            affichage.ecrire(ecran, f"{len(zones)} zone(s)  z=annuler  e=enregistrer  q=quitter", (10, 25))
        cv2.imshow(NOM_FENETRE, ecran)

        touche = cv2.waitKey(30) & 0xFF
        if etat["rectangle_en_attente"] is not None and touche in raccourcis:
            x, y, l, h = etat["rectangle_en_attente"]
            zones.append({"nom": f"Z{len(zones) + 1}", "x": x, "y": y,
                          "largeur": l, "hauteur": h, "couleur_attendue": raccourcis[touche]})
            etat["rectangle_en_attente"] = None
        elif touche == ord("z") and zones:
            zones.pop()
        elif touche == ord("e"):
            if not zones:
                print("Aucune zone à enregistrer.")
                continue
            # On ne remplace que les zones : la description du gabarit est conservée.
            gabarit = configuration.lire_json("gabarit.json")
            gabarit["zones"] = zones
            configuration.ecrire_json("gabarit.json", gabarit)
            print(f"{len(zones)} zone(s) enregistrée(s) dans config/gabarit.json")
            break
        elif touche == ord("q"):
            print("Quitté sans enregistrer.")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as erreur:
        print(f"Erreur : {erreur}")
        sys.exit(1)
