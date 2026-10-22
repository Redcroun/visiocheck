# VisioCheck

Prototype de contrôle qualité visuel par webcam (principe poka-yoke), en Python et OpenCV.

> Projet personnel réalisé avec des objets du quotidien et des données fictives.
>
> **Branche `demo-complete`** : version complète générée avec l'aide d'une IA, qui sert de démonstration et de référence.
> La branche `main` suit le parcours d'apprentissage phase par phase (voir `ROADMAP.md`).

## Objectif
Un gabarit comporte plusieurs emplacements. Chacun doit contenir une pièce d'une couleur précise.
La webcam filme le gabarit et, pour chaque emplacement, VisioCheck rend un verdict :

- **OK** : pièce présente et de la bonne couleur
- **MANQUANT** : emplacement vide
- **ERREUR** : pièce présente mais de la mauvaise couleur

puis un **verdict global OK / NOK**, tracé dans un journal CSV avec la photo de chaque NOK.

## Lien avec le terrain
_À compléter._

## Démo
_GIF ou vidéo à ajouter (phase 9)._

## Architecture
```
config/            réglages en JSON (jamais en dur dans le code)
  gabarit.json       zones (x, y, largeur, hauteur) + couleur attendue
  couleurs.json      plages HSV de chaque couleur
  reglages.json      caméra, seuil de présence, flou, chemins du journal
visiocheck/        le cœur, testable sans webcam
  detection.py       taux de pixels par couleur -> verdict par zone -> verdict global
  affichage.py       rectangles verts/rouges, bandeau OK/NOK, compteurs
  journal.py         journal CSV, photos NOK, synthèse
  camera.py          ouverture de la webcam (DirectShow + MJPG)
  configuration.py   lecture/écriture des JSON
scripts/           programmes à lancer
  main.py            contrôle en direct (espace = contrôler)
  calibrer_zones.py  dessiner les zones à la souris
  hsv_picker.py      pipette HSV pour régler les couleurs
  rapport.py         synthèse du journal
  creer_images_demo.py  images de démonstration sans webcam
tests/             tests pytest sur images synthétiques
```

**Règle de décision d'une zone** : on mesure, pour chaque couleur, la part de pixels de la zone qui tombent dans sa plage HSV.
Si aucune couleur ne dépasse le seuil de présence → MANQUANT. Si la couleur majoritaire est l'attendue → OK. Sinon → ERREUR.

## Installation
```powershell
py -3.12 -m venv .venv    # forcer Python 3.12 si plusieurs versions sont installées
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Choix de la caméra** dans `config/reglages.json` :
- webcam intégrée : `"index": 0`, `"backend": "DSHOW"` ;
- iPhone via DroidCam (réglage actuel) : `"index": 1`, `"backend": "MSMF"`.

## Utilisation
Essai sans webcam :
```powershell
python scripts/creer_images_demo.py
python scripts/main.py data/exemples/demo_nok.png
```
Avec la webcam :

Gabarit de référence à imprimer : `docs/gabarit_visiocheck_3_postit_A4.pdf`
(A4 paysage, à 100 %, la règle doit mesurer 10 cm). Il compte 3 emplacements pour
Post-it 76 x 76 mm : Z1 jaune, Z2 vert, Z3 bleu.

```powershell
python scripts/hsv_picker.py        # 1. vérifier les couleurs, ajuster config/couleurs.json
python scripts/calibrer_zones.py    # 2. dessiner les zones du gabarit
python scripts/main.py              # 3. contrôler (espace), r = direct, q = quitter
python scripts/rapport.py           # 4. synthèse du journal
```
Tests :
```powershell
python -m pytest
```

## Résultats mesurés
**Séance de test du 22/10/2026** : gabarit de référence (3 Post-it : Z1 jaune, Z2 vert, Z3 bleu),
iPhone fixe utilisé comme webcam (DroidCam, 640x480), lampe de bureau fixe.

| | Nombre |
|---|---|
| Contrôles | 10 |
| OK | 4 |
| NOK | 6 (défauts provoqués volontairement) |
| Verdicts conformes à la réalité | **10 / 10** |

- Défauts testés : Post-it manquant (Z2, Z3) et Post-it inversés entre Z1 et Z3 (erreur de montage).
- Chaque NOK a été vérifié sur sa photo : bonne zone et bonne cause (« vu : bleu », « vu : jaune »).
- Les mêmes situations ont été répétées 3 fois, avec le même verdict à chaque fois (répétabilité).

**Ce que ce résultat ne prouve pas encore** : une seule séance, un seul éclairage, un petit volume.
La mesure complète de fiabilité (30 à 50 photos, lumière variable) est prévue en phase 5.

## Limites
- Les plages HSV dépendent de l'éclairage : à recalibrer si la lumière change.
- Les zones sont fixes : le gabarit ne doit pas bouger par rapport à la caméra.
- Le noir, le blanc et le gris ne sont pas des couleurs pour le HSV : une pièce noire serait vue comme « MANQUANT ».
- Le contrôle doit être déclenché main sortie du champ : la peau peut être prise pour du jaune ou du rouge.

## Pistes d'amélioration
_À compléter._

## Ce que j'ai appris
_À compléter._
