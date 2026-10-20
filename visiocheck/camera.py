"""Ouverture de la webcam."""

import cv2

# Systèmes vidéo de Windows (« backends ») utilisables pour ouvrir la caméra.
# DSHOW : DirectShow, ancien, ouvre vite la webcam intégrée.
# MSMF  : Media Foundation, plus récent ; nécessaire pour l'iPhone via DroidCam.
BACKENDS = {
    "DSHOW": cv2.CAP_DSHOW,
    "MSMF": cv2.CAP_MSMF,
}


def ouvrir_camera(index, utiliser_mjpg=True, backend="DSHOW"):
    """Ouvre la caméra et la renvoie. Lève une erreur claire si elle ne s'ouvre pas."""
    if backend not in BACKENDS:
        raise RuntimeError(
            f"Backend caméra inconnu : {backend}. Valeurs possibles : {', '.join(BACKENDS)}."
        )
    camera = cv2.VideoCapture(index, BACKENDS[backend])
    if not camera.isOpened():
        raise RuntimeError(
            f"Impossible d'ouvrir la caméra n°{index}. Vérifie qu'elle est branchée, "
            "qu'aucune autre appli ne l'utilise, ou change l'index dans config/reglages.json."
        )
    if utiliser_mjpg:
        # Format compressé MJPG : souvent plus d'images par seconde en USB.
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    return camera


def lire_image(camera):
    """Lit une image de la caméra ; lève une erreur si la caméra ne répond plus."""
    lecture_ok, image = camera.read()
    if not lecture_ok:
        raise RuntimeError("La caméra ne renvoie plus d'image.")
    return image
