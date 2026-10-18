# VisioCheck — Feuille de route du mini-projet

> **Objectif** : construire en 2 à 3 semaines (soirées + week-ends) un mini-système de **contrôle qualité visuel par caméra** en Python/OpenCV, démontrable en vidéo et publié sur GitHub, pour appuyer ma candidature interne à la Digital Team de mon entreprise.
>
> **Message à faire passer** : « Je connais les défauts du terrain, et je sais déjà prototyper un outil de vision qui les détecte. »

---

## 1. Le cas d'usage

**Contrôle de conformité d'un kit sur gabarit** (logique poka-yoke) :

- Un gabarit (feuille A4 imprimée ou plaque LEGO) comporte **N emplacements** (4 à 8).
- Chaque emplacement doit contenir **une pièce précise, d'une couleur précise** (briques LEGO, bouchons, jetons…).
- La webcam filme le gabarit et le programme donne pour chaque emplacement un verdict :
  - ✅ **OK** : pièce présente et de la bonne couleur
  - ❌ **MANQUANT** : emplacement vide
  - ⚠️ **ERREUR** : pièce présente mais mauvaise couleur (erreur de montage)
- Un **verdict global OK / NOK** s'affiche à l'écran, avec les zones en vert ou rouge.
- Chaque contrôle est **tracé** (horodatage, verdict, zones en défaut, photo du NOK).

C'est l'analogie directe d'un contrôle présence/absence ou d'un détrompage sur ligne de montage.

### Règles non négociables

- **Aucune image, pièce, donnée ou document de l'usine.** Uniquement des objets du quotidien.
- Projet réalisé sur mon temps personnel et mon matériel personnel.
- Je dois **comprendre chaque ligne de code** : en entretien, on me demandera d'expliquer mes choix.

---

## 2. Matériel et environnement

| Élément | Choix |
|---|---|
| PC | Windows, i7, 16 Go de RAM (suffisant) |
| Caméra | Webcam intégrée ou webcam USB (meilleure : fixe et réglable) |
| Support | Webcam fixée au-dessus du gabarit (pile de livres, pince, petit trépied) |
| Éclairage | Lampe de bureau **toujours au même endroit** (clé de la fiabilité) |
| Objets | Briques LEGO ou bouchons de 3 à 4 couleurs franches |
| Optionnel (phase 7) | Arduino Uno ou ESP32 + 2 LED (vert/rouge), puis éventuellement un Raspberry Pi |

**Logiciels** : Python 3.12, VS Code, Git, compte GitHub, Codex.
**Librairies** : `opencv-python`, `numpy`, `pytest` (puis `scikit-learn` et `pyserial` en option).

---

## 3. Plan par phases

Chaque phase se termine par un **commit Git** et une coche ici.

### Phase 0 — Mise en place (1 soirée)
- [x] Installer Python 3.12, Git, VS Code (extension Python)
- [x] Créer le dépôt GitHub `visiocheck` (public), le cloner
- [x] Créer l'environnement virtuel `.venv` et `requirements.txt`
- [x] Script `scripts/test_camera.py` : afficher le flux webcam, quitter avec `q`
- [x] Premier commit

**Ce que j'apprends** : environnement Python, Git, capture vidéo OpenCV.

### Phase 1 — Les bases OpenCV (2 soirées)
- [ ] Charger une image, la convertir en niveaux de gris et en **HSV**
- [ ] Seuillage, flou, détection de contours
- [ ] Script `scripts/hsv_picker.py` : cliquer sur l'image pour lire la couleur HSV d'un pixel (sert à calibrer les couleurs)
- [ ] Noter dans `docs/notes_apprentissage.md` ce que j'ai compris (BGR vs HSV, pourquoi le HSV résiste mieux aux variations de lumière)

### Phase 2 — Configuration du gabarit (1 à 2 soirées)
- [ ] Fichier `config/gabarit.json` : liste des zones (`x, y, largeur, hauteur`) et couleur attendue pour chaque zone
- [ ] Fichier `config/couleurs.json` : plages HSV de chaque couleur
- [ ] Script `scripts/calibrer_zones.py` : dessiner les zones à la souris sur l'image et les enregistrer dans le JSON

### Phase 3 — Détection v1 (2 à 3 soirées) ⭐ cœur du projet
- [ ] Module `visiocheck/detection.py` : pour chaque zone, mesurer le pourcentage de pixels de chaque couleur
- [ ] Règles : présence si le taux dépasse un seuil ; bonne couleur si la couleur majoritaire est la couleur attendue
- [ ] Verdict par zone (OK / MANQUANT / ERREUR) et verdict global
- [ ] Affichage en direct : rectangles verts/rouges, libellés, bandeau OK/NOK
- [ ] Touche `espace` = lancer un contrôle ; touche `q` = quitter

**Livrable** : démo qui marche en direct sur ma webcam.

### Phase 4 — Traçabilité (1 à 2 soirées)
- [ ] Journal `data/controles.csv` : date/heure, verdict global, zones en défaut
- [ ] Sauvegarde automatique de la photo annotée de chaque NOK dans `data/nok/`
- [ ] Compteurs à l'écran : nombre de contrôles, OK, NOK, taux de conformité
- [ ] Script `scripts/rapport.py` : synthèse du CSV (top des zones en défaut, taux par heure)

**Lien terrain** : c'est l'équivalent du suivi qualité d'un poste. Je sais pourquoi c'est utile.

### Phase 5 — Fiabilité et tests (2 soirées)
- [ ] Constituer un jeu de **30 à 50 photos de test** dans `tests/images/` (OK, manquant, erreur de couleur, lumière variable), avec le verdict attendu dans le nom de fichier
- [ ] Tests `pytest` : le programme doit retrouver le bon verdict sur chaque photo
- [ ] Mesurer et noter le **taux de bonne détection**
- [ ] Identifier les cas d'échec (reflets, ombres) et les corriger (seuils, flou, égalisation)

**Message en entretien** : « Je ne me contente pas d'une démo qui marche une fois : je mesure la fiabilité. »

### Phase 6 — Option Machine Learning (2 à 3 soirées)
- [ ] Extraire des caractéristiques simples de chaque zone (histogramme HSV)
- [ ] Entraîner un classifieur `scikit-learn` (k-NN ou forêt aléatoire) sur mes photos étiquetées
- [ ] Comparer avec les règles de la phase 3 : précision, cas d'erreur
- [ ] Documenter la comparaison dans le README

### Phase 7 — Option embarqué / microcontrôleur (2 soirées)
- [ ] Arduino ou ESP32 relié en USB : LED verte si OK, rouge si NOK (communication série avec `pyserial`)
- [ ] Bonus : bouton physique sur l'Arduino pour déclencher le contrôle
- [ ] Bonus++ : faire tourner VisioCheck sur un Raspberry Pi (edge device)

Cette phase coche « camera control, micro contrôleurs, edge devices » de l'offre.

### Phase 8 — Option agent IA (1 à 2 soirées)
- [ ] Script `scripts/agent_synthese.py` : envoie le CSV de contrôles (données fictives) à un modèle de langage via API et obtient une **synthèse de poste** : volume, taux NOK, zone la plus problématique, piste d'action
- [ ] Prompt soigné et versionné dans `prompts/`
- [ ] Bonus : poser des questions en langage naturel sur l'historique (« Quelle zone a le plus de défauts depuis lundi ? »)

### Phase 9 — Présentation (2 soirées) ⭐ indispensable
- [ ] README soigné : objectif, lien avec le terrain, GIF de démo, architecture, installation, résultats mesurés, limites, pistes d'amélioration
- [ ] Vidéo de démo de 60 à 90 secondes (OK, manquant, erreur de couleur, LED, rapport)
- [ ] Section « Ce que j'ai appris »
- [ ] Ajouter le lien GitHub et la vidéo au CV et dans le mail de candidature

---

## 4. Planning indicatif

| Semaine | Phases | Résultat |
|---|---|---|
| 1 | 0, 1, 2 | Environnement prêt, bases OpenCV, gabarit configuré |
| 2 | 3, 4 | **Démo fonctionnelle** avec traçabilité |
| 3 | 5, 9 (+ 6, 7 ou 8 selon le temps) | Projet fiable, documenté, vidéo prête : **j'envoie la candidature** |

👉 Le **minimum viable pour candidater** = phases 0 à 5 + 9. Les phases 6, 7 et 8 sont des bonus que je peux présenter comme « en cours » en entretien.

---

## 5. Structure cible du dépôt

```
visiocheck/
├── README.md
├── ROADMAP.md
├── requirements.txt
├── config/
│   ├── gabarit.json
│   └── couleurs.json
├── visiocheck/
│   ├── __init__.py
│   ├── camera.py
│   ├── detection.py
│   ├── affichage.py
│   └── journal.py
├── scripts/
│   ├── test_camera.py
│   ├── hsv_picker.py
│   ├── calibrer_zones.py
│   ├── rapport.py
│   └── main.py
├── tests/
│   ├── images/
│   └── test_detection.py
├── data/            (ignoré par Git sauf exemples)
├── docs/
│   └── notes_apprentissage.md
└── prompts/
```

---

## 6. Comment travailler avec Codex

1. **Une phase à la fois**, une petite tâche à la fois.
2. Je demande toujours **l'explication** du code produit, ligne par ligne si besoin.
3. J'écris moi-même au moins une partie de chaque phase (les fonctions de la phase 3 en priorité).
4. Je teste avant chaque commit ; message de commit clair en français.
5. Si je ne comprends pas un morceau de code, il ne rentre pas dans le projet.

---

## 7. Préparer l'entretien avec le projet

Questions auxquelles je dois savoir répondre :

- Pourquoi le HSV plutôt que le RGB ?
- Que se passe-t-il si la lumière change ? Comment l'as-tu géré ?
- Quel est ton taux de bonne détection et comment l'as-tu mesuré ?
- Règles fixes ou machine learning : avantages et limites de chaque approche ?
- Comment adapterais-tu ce système à un vrai poste de la ligne ? (cadence, vibrations, éclairage industriel, acceptation par les opérateurs, traçabilité qualité)
- Qu'est-ce que tu ferais différemment avec plus de temps ?

La dernière partie (adapter au terrain) est **mon avantage différenciant** : la préparer avec des exemples concrets de mon expérience de Team Leader, sans divulguer d'information confidentielle.
