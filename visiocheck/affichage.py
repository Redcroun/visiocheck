"""Dessin des zones, des libellés, du bandeau OK/NOK et des compteurs sur l'image."""

import cv2

# Couleurs en BGR (ordre OpenCV : bleu, vert, rouge).
VERT = (0, 200, 0)
ROUGE = (0, 0, 230)
GRIS = (180, 180, 180)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
POLICE = cv2.FONT_HERSHEY_SIMPLEX


def ecrire(image, texte, position, couleur=BLANC, taille=0.5, epaisseur=1):
    """Écrit un texte lisible sur n'importe quel fond : pavé noir derrière, texte en couleur."""
    (largeur, hauteur), base = cv2.getTextSize(texte, POLICE, taille, epaisseur)
    x, y = position
    cv2.rectangle(image, (x - 3, y - hauteur - 4), (x + largeur + 3, y + base + 2), NOIR, -1)
    cv2.putText(image, texte, (x, y), POLICE, taille, couleur, epaisseur, cv2.LINE_AA)


def dessiner_zones(image, zones):
    """Dessine les zones en gris avec leur nom et la couleur attendue (mode attente)."""
    copie = image.copy()
    for zone in zones:
        coin1 = (zone["x"], zone["y"])
        coin2 = (zone["x"] + zone["largeur"], zone["y"] + zone["hauteur"])
        cv2.rectangle(copie, coin1, coin2, GRIS, 2)
        ecrire(copie, f'{zone["nom"]} : {zone["couleur_attendue"]}',
               (zone["x"], zone["y"] - 8), GRIS)
    return copie


def dessiner_resultat(image, zones, resultat):
    """Dessine le résultat d'un contrôle : zones vertes/rouges, libellés, bandeau global."""
    copie = image.copy()
    for zone, res in zip(zones, resultat["zones"]):
        couleur = VERT if res["verdict"] == "OK" else ROUGE
        coin1 = (zone["x"], zone["y"])
        coin2 = (zone["x"] + zone["largeur"], zone["y"] + zone["hauteur"])
        cv2.rectangle(copie, coin1, coin2, couleur, 3)
        ecrire(copie, f'{res["nom"]} {res["verdict"]}', (zone["x"], zone["y"] - 8), couleur)
        if res["verdict"] == "ERREUR":
            ecrire(copie, f'vu : {res["couleur_detectee"]}',
                   (zone["x"], zone["y"] + zone["hauteur"] + 20), couleur)
    dessiner_bandeau(copie, resultat["verdict_global"])
    return copie


def dessiner_bandeau(image, verdict_global):
    """Bandeau coloré en bas de l'image avec le verdict global."""
    hauteur, largeur = image.shape[:2]
    couleur = VERT if verdict_global == "OK" else ROUGE
    cv2.rectangle(image, (0, hauteur - 50), (largeur, hauteur), couleur, -1)
    cv2.putText(image, f"CONTROLE : {verdict_global}", (15, hauteur - 15), POLICE, 1.0, BLANC, 2, cv2.LINE_AA)


def dessiner_compteurs(image, compteurs):
    """Affiche les compteurs en haut à gauche : total, OK, NOK, taux de conformité."""
    total = compteurs["OK"] + compteurs["NOK"]
    taux = 100 * compteurs["OK"] / total if total else 0
    texte = f'Controles : {total}  OK : {compteurs["OK"]}  NOK : {compteurs["NOK"]}  Conformite : {taux:.0f} %'
    ecrire(image, texte, (10, 25))


def dessiner_aide(image, texte):
    """Affiche une ligne d'aide (touches disponibles) sous les compteurs."""
    ecrire(image, texte, (10, 50), GRIS)
