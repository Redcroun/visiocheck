"""Test de la webcam : affiche le flux vidéo avec les FPS.

Utilisation (PowerShell, venv activé) :
    python scripts/test_camera.py        # caméra n°0
    python scripts/test_camera.py 1      # autre caméra (ex. webcam USB)

Touche q : quitter.
"""

import sys
import time

import cv2

NOM_FENETRE = "VisioCheck - test camera"

# Format vidéo demandé à la webcam.
# True  : MJPG (images compressées) -> souvent bien plus de FPS en USB.
# False : format par défaut de la caméra (souvent YUY2, non compressé).
# Passe à False pour comparer les FPS avant / après.
UTILISER_MJPG = True


def lire_index_camera():
    """Renvoie l'index de caméra passé en argument, ou 0 par défaut."""
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    return 0


def ouvrir_camera(index):
    """Ouvre la caméra ; arrête le programme avec un message clair en cas d'échec."""
    # CAP_DSHOW (DirectShow) : sous Windows, la webcam s'ouvre souvent bien plus vite ainsi.
    camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not camera.isOpened():
        print(f"Erreur : impossible d'ouvrir la caméra n°{index}.")
        print("- Vérifie qu'elle est branchée et qu'aucune autre appli (Teams, Zoom…) ne l'utilise.")
        print("- Essaie un autre index : python scripts/test_camera.py 1")
        sys.exit(1)
    return camera


def demander_mjpg(camera):
    """Demande à la caméra d'envoyer ses images au format compressé MJPG."""
    # Un « FOURCC » est un code de 4 lettres qui désigne un format vidéo.
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))


def decrire_format(camera):
    """Renvoie un texte décrivant le format réellement utilisé par la caméra."""
    code = int(camera.get(cv2.CAP_PROP_FOURCC))
    # Le code est un nombre qui contient 4 lettres : on les extrait une par une.
    lettres = "".join(chr((code >> 8 * i) & 0xFF) for i in range(4))
    largeur = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    hauteur = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return f"format {lettres}, {largeur}x{hauteur}"


def main():
    index = lire_index_camera()
    camera = ouvrir_camera(index)
    if UTILISER_MJPG:
        demander_mjpg(camera)
    print(f"Caméra ouverte ({decrire_format(camera)}).")
    print("Appuie sur q dans la fenêtre vidéo pour quitter.")

    instant_precedent = time.perf_counter()
    fps = 0.0

    while True:
        lecture_ok, image = camera.read()
        if not lecture_ok:
            print("Erreur : la caméra ne renvoie plus d'image.")
            break

        # Calcul des FPS : 1 / durée entre deux images, lissé pour éviter que le chiffre saute.
        maintenant = time.perf_counter()
        fps_instantane = 1.0 / (maintenant - instant_precedent)
        instant_precedent = maintenant
        fps = 0.9 * fps + 0.1 * fps_instantane

        cv2.putText(image, f"FPS : {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.imshow(NOM_FENETRE, image)

        touche = cv2.waitKey(1) & 0xFF
        if touche == ord("q"):
            break
        # Fermeture de la fenêtre avec la croix : on quitte aussi.
        if cv2.getWindowProperty(NOM_FENETRE, cv2.WND_PROP_VISIBLE) < 1:
            break

    print(f"FPS moyen en fin de test : {fps:.1f}")
    camera.release()
    cv2.destroyAllWindows()
    print("Caméra libérée, fin du test.")


if __name__ == "__main__":
    main()
