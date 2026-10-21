"""Tests de la détection et du journal sur des images synthétiques (sans webcam).

Lancer : python -m pytest
"""

import cv2
import numpy as np
import pytest

from visiocheck import detection, journal

# Plages HSV propres aux tests : elles ne dépendent pas de config/couleurs.json.
# Tu peux donc régler config/couleurs.json pour ta caméra sans casser les tests.
COULEURS = {
    "rouge": {"plages": [{"min": [0, 100, 70], "max": [10, 255, 255]},
                         {"min": [170, 100, 70], "max": [179, 255, 255]}]},
    "jaune": {"plages": [{"min": [20, 100, 100], "max": [35, 255, 255]}]},
    "vert": {"plages": [{"min": [40, 70, 50], "max": [85, 255, 255]}]},
    "bleu": {"plages": [{"min": [95, 100, 50], "max": [130, 255, 255]}]},
}
SEUIL = 0.30

ZONES = [
    {"nom": "Z1", "x": 10, "y": 10, "largeur": 80, "hauteur": 80, "couleur_attendue": "rouge"},
    {"nom": "Z2", "x": 110, "y": 10, "largeur": 80, "hauteur": 80, "couleur_attendue": "vert"},
    {"nom": "Z3", "x": 210, "y": 10, "largeur": 80, "hauteur": 80, "couleur_attendue": "bleu"},
]

BGR = {"rouge": (0, 0, 220), "vert": (0, 170, 0), "bleu": (200, 60, 0), "jaune": (0, 220, 230)}


def image_avec_pieces(pieces):
    """Fond clair + une pièce pleine dans chaque zone (None = emplacement vide)."""
    image = np.full((100, 300, 3), 235, dtype=np.uint8)
    for zone in ZONES:
        couleur = pieces.get(zone["nom"])
        if couleur:
            x, y = zone["x"] + 10, zone["y"] + 10
            cv2.rectangle(image, (x, y), (x + 60, y + 60), BGR[couleur], -1)
    return image


def controler(pieces):
    return detection.controler_image(image_avec_pieces(pieces), ZONES, COULEURS, SEUIL)


def verdicts(resultat):
    return [r["verdict"] for r in resultat["zones"]]


def test_tout_conforme_donne_ok():
    resultat = controler({"Z1": "rouge", "Z2": "vert", "Z3": "bleu"})
    assert verdicts(resultat) == ["OK", "OK", "OK"]
    assert resultat["verdict_global"] == "OK"


def test_emplacement_vide_donne_manquant():
    resultat = controler({"Z1": "rouge", "Z2": None, "Z3": "bleu"})
    assert verdicts(resultat) == ["OK", "MANQUANT", "OK"]
    assert resultat["verdict_global"] == "NOK"


def test_mauvaise_couleur_donne_erreur():
    resultat = controler({"Z1": "rouge", "Z2": "vert", "Z3": "jaune"})
    assert verdicts(resultat) == ["OK", "OK", "ERREUR"]
    assert resultat["zones"][2]["couleur_detectee"] == "jaune"


def test_rouge_cote_179_est_bien_reconnu():
    # Un rouge légèrement violacé a un H proche de 179 : il doit rester « rouge ».
    image = image_avec_pieces({"Z2": "vert", "Z3": "bleu"})
    cv2.rectangle(image, (20, 20), (80, 80), (40, 0, 220), -1)
    resultat = detection.controler_image(image, ZONES, COULEURS, SEUIL)
    assert resultat["zones"][0]["verdict"] == "OK"


def test_decider_verdict_regles():
    assert detection.decider_verdict({"rouge": 0.1, "vert": 0.05}, "rouge", 0.3) == ("MANQUANT", None)
    assert detection.decider_verdict({"rouge": 0.6, "vert": 0.05}, "rouge", 0.3) == ("OK", "rouge")
    assert detection.decider_verdict({"rouge": 0.1, "vert": 0.7}, "rouge", 0.3) == ("ERREUR", "vert")


def test_journal_et_synthese(tmp_path):
    chemin = tmp_path / "controles.csv"
    ok = controler({"Z1": "rouge", "Z2": "vert", "Z3": "bleu"})
    nok = controler({"Z1": "rouge", "Z2": None, "Z3": "jaune"})
    journal.enregistrer_controle(chemin, ok, "2026-10-19 14:00:00")
    journal.enregistrer_controle(chemin, nok, "2026-10-19 14:05:00")
    journal.enregistrer_controle(chemin, nok, "2026-10-19 15:10:00")

    lignes = journal.lire_journal(chemin)
    assert len(lignes) == 3
    assert lignes[1]["zones_en_defaut"] == "Z2,Z3"

    synthese = journal.calculer_synthese(lignes)
    assert synthese["total"] == 3
    assert synthese["nok"] == 2
    assert round(synthese["taux_conformite"]) == 33
    assert synthese["top_zones"][0] == ("Z2", 2)
    assert synthese["par_heure"]["14h"] == {"total": 2, "OK": 1}


def test_journal_utilise_le_point_virgule_pour_excel(tmp_path):
    chemin = tmp_path / "controles.csv"
    journal.enregistrer_controle(chemin, controler({"Z1": "rouge", "Z2": None, "Z3": "bleu"}),
                                 "2026-10-20 19:00:00")
    premiere_ligne = chemin.read_text(encoding="utf-8-sig").splitlines()[0]
    assert premiere_ligne == "horodatage;verdict_global;zones_en_defaut;detail;photo"


def test_echec_d_ecriture_d_image_est_signale(tmp_path):
    # Dossier inexistant : cv2.imwrite renvoie False au lieu de planter.
    chemin = tmp_path / "dossier_absent" / "photo.jpg"
    with pytest.raises(RuntimeError):
        journal.ecrire_image(chemin, np.zeros((10, 10, 3), dtype=np.uint8))


def test_journal_note_le_nom_de_la_photo(tmp_path):
    chemin = tmp_path / "controles.csv"
    nok = controler({"Z1": "rouge", "Z2": None, "Z3": "bleu"})
    journal.enregistrer_controle(chemin, nok, "2026-10-21 19:40:00", "nok_2026-10-21_19-40-00.jpg")
    journal.enregistrer_controle(chemin, controler({"Z1": "rouge", "Z2": "vert", "Z3": "bleu"}),
                                 "2026-10-21 19:41:00")
    lignes = journal.lire_journal(chemin)
    assert lignes[0]["photo"] == "nok_2026-10-21_19-40-00.jpg"
    assert lignes[1]["photo"] == ""


def test_ancien_format_de_journal_est_refuse(tmp_path):
    chemin = tmp_path / "controles.csv"
    chemin.write_text("horodatage;verdict_global;zones_en_defaut;detail\n", encoding="utf-8-sig")
    with pytest.raises(RuntimeError):
        journal.enregistrer_controle(chemin, controler({"Z1": "rouge", "Z2": "vert", "Z3": "bleu"}),
                                     "2026-10-21 19:42:00")
