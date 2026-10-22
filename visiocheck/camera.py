"""Ouverture de la webcam."""

import time

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


# Tolérance aux coupures courtes (ex. iPhone en Wi-Fi via DroidCam qui rate une image) :
# on réessaie jusqu'à 30 fois, toutes les 0,03 s, soit environ 1 seconde avant d'abandonner.
NB_ESSAIS_LECTURE = 30
PAUSE_ENTRE_ESSAIS = 0.03


def lire_image(camera):
    """Lit une image de la caméra.

    Une image ratée de temps en temps est normale : on réessaie quelques fois.
    On ne lève une erreur que si la caméra reste muette pendant environ 1 seconde.
    """
    for _ in range(NB_ESSAIS_LECTURE):
        lecture_ok, image = camera.read()
        if lecture_ok:
            return image
        time.sleep(PAUSE_ENTRE_ESSAIS)
    raise RuntimeError("La caméra ne renvoie plus d'image depuis environ 1 seconde "
                       "(caméra débranchée, DroidCam arrêté ou Wi-Fi coupé ?).")


def charger_image_fichier(chemin):
    """Lit une image depuis un fichier ; lève une erreur claire si c'est impossible."""
    image = cv2.imread(str(chemin))
    if image is None:
        raise RuntimeError(f"Impossible de lire l'image {chemin} (chemin ou format incorrect).")
    return image


def ouvrir_source(arguments, reglages_camera):
    """Choisit la source d'images des scripts.

    - un chemin d'image est passé en argument -> on travaille sur ce fichier ;
    - sinon -> on ouvre la caméra décrite dans config/reglages.json.
    Renvoie (image_fichier, camera) : l'un des deux vaut None.
    """
    if arguments:
        return charger_image_fichier(arguments[0]), None
    camera = ouvrir_camera(reglages_camera["index"], reglages_camera["utiliser_mjpg"],
                           reglages_camera["backend"])
    return None, camera


def image_suivante(image_fichier, camera):
    """Renvoie l'image à traiter : l'image fichier (toujours la même) ou une nouvelle image caméra."""
    if image_fichier is not None:
        return image_fichier
    return lire_image(camera)


def liberer(camera):
    """Libère la caméra si elle a été ouverte (rien à faire pour une image fichier)."""
    if camera is not None:
        camera.release()
