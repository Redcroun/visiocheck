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
from visiocheck.camera import lire_image, ouvrir_camera

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

    # Source d'images : un fichier passé en argument, sinon la webcam.
    image_fichier = None
    camera = None
    if len(sys.argv) > 1:
        image_fichier = cv2.imread(sys.argv[1])
        if image_fichier is None:
            print(f"Erreur : impossible de lire l'image {sys.argv[1]}")
            sys.exit(1)
    else:
        try:
            camera = ouvrir_camera(reglages["camera"]["index"], reglages["camera"]["utiliser_mjpg"])
        except RuntimeError as erreur:
            print(f"Erreur : {erreur}")
            sys.exit(1)

    print("VisioCheck démarré. " + AIDE)
    resultat_affiche = None  # image annotée du dernier contrôle, figée à l'écran

    while True:
        image = image_fichier if image_fichier is not None else lire_image(camera)

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

    if camera is not None:
        camera.release()
    cv2.destroyAllWindows()
    total = compteurs["OK"] + compteurs["NOK"]
    print(f"Fin : {total} contrôle(s), {compteurs['OK']} OK, {compteurs['NOK']} NOK.")


if __name__ == "__main__":
    main()
