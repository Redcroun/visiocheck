"""Tests de la lecture caméra avec une fausse caméra (pas besoin de webcam)."""

import numpy as np
import pytest

from visiocheck import camera


class FausseCamera:
    """Imite cv2.VideoCapture : rate `nb_echecs` lectures, puis renvoie une image."""

    def __init__(self, nb_echecs):
        self.nb_echecs = nb_echecs

    def read(self):
        if self.nb_echecs > 0:
            self.nb_echecs -= 1
            return False, None
        return True, np.zeros((480, 640, 3), dtype=np.uint8)


def test_quelques_images_ratees_sont_tolerees(monkeypatch):
    monkeypatch.setattr(camera, "PAUSE_ENTRE_ESSAIS", 0)  # test rapide : pas d'attente
    image = camera.lire_image(FausseCamera(nb_echecs=5))
    assert image.shape == (480, 640, 3)


def test_camera_muette_leve_une_erreur(monkeypatch):
    monkeypatch.setattr(camera, "PAUSE_ENTRE_ESSAIS", 0)
    with pytest.raises(RuntimeError):
        camera.lire_image(FausseCamera(nb_echecs=1000))
