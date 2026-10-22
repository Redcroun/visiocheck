"""Test de la caméra : affiche le flux vidéo, son format réel et les FPS.

La caméra utilisée est celle de config/reglages.json (index, backend, MJPG),
c'est-à-dire exactement la même que pour main.py, calibrer_zones.py et hsv_picker.py.

Utilisation (PowerShell, venv activé) :
    python scripts/test_camera.py        # caméra de config/reglages.json
    python scripts/test_camera.py 0      # forcer un autre index (ex. webcam intégrée)

Touche q ou croix de la fenêtre : quitter.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

from visiocheck import affichage, configuration
from visiocheck.camera import liberer, lire_image, ouvrir_camera

NOM_FENETRE = "VisioCheck - test camera"


def decrire_format(camera):
    """Renvoie un texte décrivant le format réellement utilisé par la caméra."""
    code = int(camera.get(cv2.CAP_PROP_FOURCC))
    # Le code est un nombre qui contient 4 lettres : on les extrait une par une.
    lettres = "".join(chr((code >> 8 * i) & 0xFF) for i in range(4))
    largeur = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    hauteur = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return f"format {lettres}, {largeur}x{hauteur}"


def lire_index(index_par_defaut):
    """Renvoie l'index passé en argument (pratique pour essayer une autre caméra), sinon celui des réglages."""
    if len(sys.argv) < 2:
        return index_par_defaut
    if not sys.argv[1].isdigit():
        raise RuntimeError(f"L'index de caméra doit être un nombre (ex. 0 ou 1), pas « {sys.argv[1]} ».")
    return int(sys.argv[1])


def main():
    reglages_camera = configuration.charger_reglages()["camera"]
    index = lire_index(reglages_camera["index"])
    camera = ouvrir_camera(index, reglages_camera["utiliser_mjpg"], reglages_camera["backend"])
    print(f"Caméra n°{index} ouverte en {reglages_camera['backend']} ({decrire_format(camera)}).")
    print("Appuie sur q dans la fenêtre vidéo pour quitter.")

    instant_precedent = time.perf_counter()
    fps = 0.0
    while True:
        image = lire_image(camera)

        # FPS : 1 / durée entre deux images, lissé pour éviter que le chiffre saute.
        # Attention : avec MSMF, la même image peut être relue plusieurs fois,
        # ce chiffre mesure alors la vitesse de la boucle (voir docs/notes_apprentissage.md).
        maintenant = time.perf_counter()
        fps = 0.9 * fps + 0.1 / (maintenant - instant_precedent)
        instant_precedent = maintenant

        affichage.ecrire(image, f"FPS : {fps:.1f}", (10, 30), affichage.VERT, 0.8, 2)
        cv2.imshow(NOM_FENETRE, image)
        if cv2.waitKey(1) & 0xFF == ord("q") or affichage.fenetre_fermee(NOM_FENETRE):
            break

    print(f"FPS moyen en fin de test : {fps:.1f}")
    liberer(camera)
    cv2.destroyAllWindows()
    print("Caméra libérée, fin du test.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as erreur:
        print(f"Erreur : {erreur}")
        sys.exit(1)
