"""Tests de la vérification du gabarit (config/gabarit.json) avant un contrôle."""

from visiocheck.configuration import verifier_gabarit

COULEURS = {"rouge": {}, "vert": {}, "bleu": {}}  # seuls les noms comptent ici
LARGEUR, HAUTEUR = 640, 480


def zone(nom="Z1", x=10, y=10, largeur=80, hauteur=80, couleur="rouge"):
    return {"nom": nom, "x": x, "y": y, "largeur": largeur, "hauteur": hauteur,
            "couleur_attendue": couleur}


def test_gabarit_correct_ne_signale_rien():
    zones = [zone("Z1"), zone("Z2", x=100, couleur="vert")]
    assert verifier_gabarit(zones, COULEURS, LARGEUR, HAUTEUR) == []


def test_zone_hors_image_est_signalee():
    # Cas réel : gabarit calibré en 1280x720, puis caméra en 640x480.
    problemes = verifier_gabarit([zone("Z3", x=900)], COULEURS, LARGEUR, HAUTEUR)
    assert len(problemes) == 1
    assert "Z3" in problemes[0] and "sort de l'image" in problemes[0]


def test_couleur_inconnue_est_signalee():
    # Cas réel : faute de frappe « Rouge » au lieu de « rouge ».
    problemes = verifier_gabarit([zone("Z1", couleur="Rouge")], COULEURS, LARGEUR, HAUTEUR)
    assert len(problemes) == 1
    assert "Rouge" in problemes[0] and "inconnue" in problemes[0]


def test_gabarit_vide_est_signale():
    problemes = verifier_gabarit([], COULEURS, LARGEUR, HAUTEUR)
    assert "aucune zone" in problemes[0]
