# Notes d'apprentissage

Ce que j'ai compris, phase par phase, pour pouvoir le réexpliquer à l'oral.

## Phase 0 — Caméra

### Les backends vidéo sous Windows

- **Résumé oral** : sous Windows, OpenCV peut ouvrir une caméra par plusieurs « backends », c'est-à-dire plusieurs systèmes vidéo du système d'exploitation. Les deux principaux sont DirectShow (`cv2.CAP_DSHOW`, ancien) et Media Foundation (`cv2.CAP_MSMF`, plus récent). Une caméra qui ne s'ouvre pas avec l'un peut fonctionner avec l'autre.
- **Mon cas concret** : mon iPhone 13, utilisé comme webcam via DroidCam (Wi-Fi), plantait avec DirectShow à l'index 1, mais s'ouvre sans problème avec Media Foundation. La webcam intégrée, elle, est à l'index 0 et marche avec les deux.
- **Méthode** : plutôt que de tester au hasard, j'ai utilisé `scripts/trouver_camera.py` (écrit avec l'aide de Claude), qui essaie chaque combinaison index / backend et affiche celles qui renvoient une image. Le backend utilisé est choisi par la constante `BACKEND_CAMERA` dans `scripts/test_camera.py`.

### Attention à la mesure des FPS

- Avec l'iPhone, le script affiche environ 80 FPS, alors que DroidCam envoie en pratique beaucoup moins d'images par seconde.
- Explication probable : avec Media Foundation, `camera.read()` peut renvoyer plusieurs fois la même image si aucune nouvelle n'est arrivée. Mon calcul mesure donc la vitesse de la boucle Python, pas le nombre de vraies nouvelles images.
- Pour VisioCheck, ce n'est pas un problème : le contrôle porte sur un gabarit immobile et se déclenche à la demande. Pour une vraie mesure, il faudrait comparer les images successives.
