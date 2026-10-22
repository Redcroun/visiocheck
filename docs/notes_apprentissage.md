# Notes d'apprentissage

Ce que j'ai compris, phase par phase, pour pouvoir le réexpliquer à l'oral.

## Comment VisioCheck décide (détection)

### Le chemin d'une image
- **Résumé oral** : à chaque appui sur espace, VisioCheck prend une photo, la floute légèrement pour effacer le bruit du capteur, puis la convertit en HSV. Pour chaque zone du gabarit, il mesure la part de pixels de chaque couleur, applique trois règles simples, puis rend un verdict par zone et un verdict global.

### Pourquoi le HSV plutôt que le RGB
- **Résumé oral** : en RGB, une même pièce change complètement de valeurs quand la lumière baisse, car les trois canaux baissent ensemble. En HSV, la teinte (H) dit « quelle couleur », la saturation (S) « couleur vive ou délavée », la luminosité (V) « clair ou sombre ». Quand la lumière change, c'est surtout V qui bouge : la teinte reste stable, donc la couleur se reconnaît mieux.
- **Piège** : dans OpenCV, H va de 0 à 179 (et non 0 à 360). Le rouge est à cheval sur le début et la fin de l'échelle (vers 0 et vers 179) : il lui faut deux plages.
- **Limite** : le noir, le blanc et le gris n'ont pas de teinte (S trop faible). Ils ne sont reconnus comme aucune couleur.

### La règle de décision d'une zone
- **Résumé oral** : si aucune couleur ne couvre au moins 30 % de la zone, l'emplacement est vide : MANQUANT. Si la couleur majoritaire est celle attendue : OK. Sinon : ERREUR, avec la couleur vue. Une seule zone en défaut suffit pour que le gabarit soit NOK.

### Règles fixes plutôt que machine learning
- **Résumé oral** : pour un détrompage de couleur sur un gabarit fixe, des règles simples suffisent, s'expliquent en une phrase et se règlent dans un fichier. Le machine learning devient utile quand les cas sont trop variés pour être décrits par des seuils (formes, textures, défauts d'aspect). On commence par le plus simple qui marche, et on mesure.

## Test réel du 22/10/2026

### Déroulé et résultat
- Gabarit imprimé (3 Post-it), iPhone fixe via DroidCam, lampe fixe.
- Mesure des couleurs avec `hsv_picker.py` : jaune H=32, vert H=43, bleu H=93, papier S=5.
- 10 contrôles : 4 OK, 6 NOK provoqués (Post-it manquant, Post-it inversés). **10 verdicts conformes sur 10**, chaque NOK vérifié sur sa photo.

### Ce que j'ai appris
- **Calibrer sur des mesures réelles** : mon bleu (H=93) sortait de la plage prévue (95-130). Sans mesure préalable, il aurait été vu comme MANQUANT. J'ai déplacé les frontières en gardant une marge d'environ 5 de chaque côté de chaque mesure.
- **Répétabilité** : les mêmes situations répétées 3 fois donnent le même verdict. C'est la première brique d'une mesure de fiabilité.
- **Coupures caméra** : en Wi-Fi, DroidCam rate parfois une image. Le programme réessaie pendant environ 1 seconde avant d'abandonner, au lieu de s'arrêter au premier raté.
- **Lien terrain** : le contrôle se déclenche main sortie du champ, comme sur une ligne où l'on déclenche par un capteur ou un bouton une fois l'opérateur sorti de la zone.
