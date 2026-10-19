"""Détection par zone : présence et couleur de la pièce.

Tout fonctionne sur une image numpy (BGR), sans webcam :
on peut donc tester ce module avec pytest sur des images fixes.
"""

import cv2
import numpy as np

OK = "OK"
MANQUANT = "MANQUANT"
ERREUR = "ERREUR"


def preparer_image(image_bgr, taille_flou):
    """Floute légèrement l'image puis la convertit en HSV.

    Le flou gomme le bruit du capteur (pixels isolés de couleur parasite).
    La taille du flou doit être impaire (3, 5, 7...).
    """
    if taille_flou > 1:
        image_bgr = cv2.GaussianBlur(image_bgr, (taille_flou, taille_flou), 0)
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)


def extraire_zone(image, zone):
    """Découpe le rectangle de la zone dans l'image (même principe qu'un slice de tableau)."""
    x, y = zone["x"], zone["y"]
    return image[y:y + zone["hauteur"], x:x + zone["largeur"]]


def masque_couleur(zone_hsv, plages):
    """Renvoie un masque noir et blanc : blanc là où le pixel est dans une des plages."""
    masque = np.zeros(zone_hsv.shape[:2], dtype=np.uint8)
    for plage in plages:
        bas = np.array(plage["min"], dtype=np.uint8)
        haut = np.array(plage["max"], dtype=np.uint8)
        # Plusieurs plages possibles (le rouge est coupé en deux) : on les additionne.
        masque = cv2.bitwise_or(masque, cv2.inRange(zone_hsv, bas, haut))
    return masque


def mesurer_taux_couleurs(zone_hsv, couleurs):
    """Pour chaque couleur connue, renvoie la part de pixels de la zone (entre 0 et 1)."""
    nb_pixels = zone_hsv.shape[0] * zone_hsv.shape[1]
    taux = {}
    for nom, definition in couleurs.items():
        masque = masque_couleur(zone_hsv, definition["plages"])
        taux[nom] = cv2.countNonZero(masque) / nb_pixels
    return taux


def decider_verdict(taux, couleur_attendue, seuil_presence):
    """Applique les règles de décision d'une zone.

    - aucune couleur ne dépasse le seuil      -> MANQUANT
    - la couleur majoritaire est l'attendue   -> OK
    - sinon                                   -> ERREUR (mauvaise pièce)
    Renvoie (verdict, couleur_detectee).
    """
    couleur_majoritaire = max(taux, key=taux.get)
    if taux[couleur_majoritaire] < seuil_presence:
        return MANQUANT, None
    if couleur_majoritaire == couleur_attendue:
        return OK, couleur_majoritaire
    return ERREUR, couleur_majoritaire


def controler_image(image_bgr, zones, couleurs, seuil_presence, taille_flou=5):
    """Contrôle toutes les zones d'une image et renvoie le résultat complet.

    Résultat : {"verdict_global": "OK" ou "NOK", "zones": [ {...}, ... ]}
    """
    image_hsv = preparer_image(image_bgr, taille_flou)
    resultats_zones = []
    for zone in zones:
        taux = mesurer_taux_couleurs(extraire_zone(image_hsv, zone), couleurs)
        verdict, couleur_detectee = decider_verdict(
            taux, zone["couleur_attendue"], seuil_presence)
        resultats_zones.append({
            "nom": zone["nom"],
            "verdict": verdict,
            "couleur_attendue": zone["couleur_attendue"],
            "couleur_detectee": couleur_detectee,
            "taux": taux,
        })
    tout_ok = all(r["verdict"] == OK for r in resultats_zones)
    return {"verdict_global": "OK" if tout_ok else "NOK", "zones": resultats_zones}


def zones_en_defaut(resultat):
    """Renvoie la liste des zones dont le verdict n'est pas OK."""
    return [r for r in resultat["zones"] if r["verdict"] != OK]
