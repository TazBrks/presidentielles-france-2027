# Présidentielles françaises : analyse 2002-2022 et tendance 2027

Projet final du cours **Programming for Data Science**.

## Objectif

Analyser les résultats des élections présidentielles françaises de 2002 à 2022
(par bureau de vote) selon trois dimensions : le temps, l'espace et l'analytique,
puis dégager une tendance pour 2027. Le projet suit le processus KDD.

## Sources de données

- data.gouv.fr : « Données des élections agrégées » (2002-2022, par bureau de vote)
- data.gouv.fr : « Présidentielle 2027 : sondages, candidatures et projection départementale »
- INSEE : statistiques locales et séries temporelles
- ACLED : événements en France (depuis 2020)
- API REST Wikimedia

## Récupérer les données

Les données brutes ne sont pas versionnées. Les placer dans `data/raw/` :

| Fichier | Source |
|---|---|
| `general_results.parquet` | [data.gouv.fr, Données des élections agrégées](https://www.data.gouv.fr/datasets/donnees-des-elections-agregees) |
| `candidats_results.parquet` | même page |
| 8 CSV des sondages 2027 (`sondages-presidentielle-2027.csv`, `projection-departementale-1er-tour.csv`, etc.) | [data.gouv.fr, Présidentielle 2027 : sondages, candidatures et projection départementale](https://www.data.gouv.fr/datasets/presidentielle-2027-sondages-candidatures-et-projection-departementale) |
| export ACLED (CSV) | [ACLED Data Export Tool](https://acleddata.com), France, depuis 2020 |

Les tables `data/reference/candidats_familles.csv` (2002-2022) et
`candidats_familles_2027.csv` associent chaque candidat à une famille politique, pour comparer les élections entre elles.
Les contours des départements (`data/reference/departements.geojson`) viennent de
[france-geojson](https://github.com/gregoiredavid/france-geojson).

## Structure

```
data/
  raw/          données brutes (non versionnées)
  processed/    données nettoyées (générées par le notebook)
  reference/    tables de référence (familles politiques)
notebooks/      notebook principal presidentielles.ipynb (fonctions + main)
dashboard/      application Dash
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancer le dashboard

```bash
python dashboard/app.py
```

## Tendance 2027

Pour chaque département et chaque famille politique, le notebook calcule l'écart
au score national entre 2002 et 2022, le prolonge jusqu'en 2027 par régression
linéaire, puis l'applique au sondage de référence. Le résultat est comparé à la
projection départementale publiée avec les sondages. C'est une tendance, pas une
prévision.
