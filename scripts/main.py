"""Programme principal VisioCheck : contrôle qualité en direct.

Utilisation (PowerShell, venv activé, depuis la racine du projet) :
    python scripts/main.py                                  # avec la webcam
    python scripts/main.py data/exemples/demo_nok.png       # sur une image fichier

Touches : espace = lancer un contrôle, r = revenir au direct, q = quitter.
"""

import sys
from pathlib import Path

# Permet d'importer le dossier visiocheck/ quand on lance le script depuis scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

from visiocheck import affichage, configuration, detection, journal
from visiocheck.camera import image_suivante, liberer, ouvrir_source

NOM_FENETRE = "VisioCheck"
AIDE = "espace : controler   r : direct   q : quitter"


def controler(image, zones, couleurs, reglages, compteurs):
    """Lance un contrôle, met à jour compteurs et journal, renvoie l'image annotée."""
    regl_detection = reglages["detection"]
    resultat = detection.controler_image(
        image, zones, couleurs,
        regl_detection["seuil_presence"], regl_detection["taille_flou"])
    compteurs[resultat["verdict_global"]] += 1

    image_annotee = affichage.dessiner_resultat(image, zones, resultat)
    horodatage = journal.maintenant()
    regl_journal = reglages["journal"]
    journal.enregistrer_controle(
        configuration.chemin_projet(regl_journal["fichier_csv"]), resultat, horodatage)

    if resultat["verdict_global"] == "NOK":
        chemin = journal.sauvegarder_photo_nok(
            configuration.chemin_projet(regl_journal["dossier_nok"]), image_annotee, horodatage)
        defauts = ", ".join(f'{r["nom"]} {r["verdict"]}' for r in detection.zones_en_defaut(resultat))
        print(f"{horodatage}  NOK ({defauts})  photo : {chemin.name}")
    else:
        print(f"{horodatage}  OK")
    return image_annotee


def fenetre_fermee():
    """Vrai si l'utilisateur a fermé la fenêtre avec la croix."""
    return cv2.getWindowProperty(NOM_FENETRE, cv2.WND_PROP_VISIBLE) < 1


def main():
    zones = configuration.charger_zones()
    couleurs = configuration.charger_couleurs()
    reglages = configuration.charger_reglages()
    compteurs = {"OK": 0, "NOK": 0}

    # Source d'images : un fichier passé en argument, sinon la caméra.
    image_fichier, camera = ouvrir_source(sys.argv[1:], reglages["camera"])

    # On vérifie le gabarit sur une 1re image : couleurs connues, zones dans l'image.
    premiere_image = image_suivante(image_fichier, camera)
    hauteur, largeur = premiere_image.shape[:2]
    problemes = configuration.verifier_gabarit(zones, couleurs, largeur, hauteur)
    if problemes:
        liberer(camera)
        raise RuntimeError("config/gabarit.json est incorrect :\n- " + "\n- ".join(problemes))

    print("VisioCheck démarré. " + AIDE)
    resultat_affiche = None  # image annotée du dernier contrôle, figée à l'écran

    while True:
        image = image_suivante(image_fichier, camera)

        if resultat_affiche is not None:
            ecran = resultat_affiche.copy()
        else:
            ecran = affichage.dessiner_zones(image, zones)
        affichage.dessiner_compteurs(ecran, compteurs)
        affichage.dessiner_aide(ecran, AIDE)
        cv2.imshow(NOM_FENETRE, ecran)

        touche = cv2.waitKey(30) & 0xFF
        if touche == ord("q") or fenetre_fermee():
            break
        if touche == ord(" "):
            resultat_affiche = controler(image, zones, couleurs, reglages, compteurs)
        if touche == ord("r"):
            resultat_affiche = None

    liberer(camera)
    cv2.destroyAllWindows()
    total = compteurs["OK"] + compteurs["NOK"]
    print(f"Fin : {total} contrôle(s), {compteurs['OK']} OK, {compteurs['NOK']} NOK.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as erreur:
        print(f"Erreur : {erreur}")
        sys.exit(1)
