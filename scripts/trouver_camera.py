"""Teste les index de caméra 0 à 3 avec deux backends Windows
(DirectShow et Media Foundation) et indique lesquels renvoient une image."""
import cv2

BACKENDS = {
    "DSHOW": cv2.CAP_DSHOW,  # DirectShow : ancien système vidéo de Windows
    "MSMF": cv2.CAP_MSMF,    # Media Foundation : système plus récent
}

for nom_backend, backend in BACKENDS.items():
    print(f"--- Backend {nom_backend} ---")
    for index in range(4):
        camera = cv2.VideoCapture(index, backend)
        ok, image = camera.read()
        if ok:
            hauteur, largeur = image.shape[:2]
            print(f"Index {index} : image reçue ({largeur}x{hauteur})")
        else:
            print(f"Index {index} : rien")
        camera.release()
