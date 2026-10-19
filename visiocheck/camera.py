"""Ouverture de la webcam."""

import cv2


def ouvrir_camera(index, utiliser_mjpg=True):
    """Ouvre la caméra et la renvoie. Lève une erreur claire si elle ne s'ouvre pas."""
    # CAP_DSHOW (DirectShow) : sous Windows, la webcam s'ouvre souvent plus vite ainsi.
    camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
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
