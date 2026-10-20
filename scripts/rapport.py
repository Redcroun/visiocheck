"""Synthèse du journal des contrôles (data/controles.csv).

Utilisation :
    python scripts/rapport.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from visiocheck import configuration, journal


def main():
    reglages = configuration.charger_reglages()
    chemin_csv = configuration.chemin_projet(reglages["journal"]["fichier_csv"])
    if not chemin_csv.exists():
        print(f"Aucun journal trouvé ({chemin_csv}). Lance d'abord quelques contrôles avec scripts/main.py.")
        return

    synthese = journal.calculer_synthese(journal.lire_journal(chemin_csv))

    print("=== Synthèse VisioCheck ===")
    print(f"Contrôles : {synthese['total']}   OK : {synthese['ok']}   NOK : {synthese['nok']}")
    print(f"Taux de conformité : {synthese['taux_conformite']:.1f} %")

    print("\nZones les plus en défaut :")
    if not synthese["top_zones"]:
        print("  aucune")
    for zone, nombre in synthese["top_zones"]:
        print(f"  {zone} : {nombre} défaut(s)")

    print("\nConformité par heure :")
    for heure, compte in synthese["par_heure"].items():
        taux = 100 * compte["OK"] / compte["total"]
        print(f"  {heure} : {compte['total']} contrôle(s), {taux:.0f} % OK")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as erreur:
        print(f"Erreur : {erreur}")
        sys.exit(1)
