# Présidentielles françaises : analyse 2002-2022 et tendance 2027

Projet final du cours **Programming for Data Science**.

Équipe : Manel HASSAN, Tasnim BOURKHIS (cheffe d'équipe), Julia PLAYE-LORENTE, Marie BARDET, Inès BENBARA, Karell Steve JODOM CHOUDJA.

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
| `sondages.json` (29 sondages 2027, toutes hypothèses) | data.gouv.fr, sondages d'intentions de vote 2027 |
| `communes-france-2026.parquet` | [data.gouv.fr, liste des communes de France](https://www.data.gouv.fr/datasets/6745d9ae4524d845d2138193) |
| `FILOSOFI_CC_csv.zip` | [INSEE, Filosofi 2023](https://www.insee.fr/fr/statistiques/8984752) |
| `TD_IMG1A_2022_csv.zip` (facultatif : déjà agrégé dans `data/reference/immigres_departements_2022.csv`) | [INSEE, recensement 2022, immigration](https://www.insee.fr/fr/statistiques/8582054?sommaire=8582058) |
| `serie_001759970_*.zip` (indice des prix) | [INSEE, série 001759970](https://www.insee.fr/fr/statistiques/serie/001759970) |
| `acled_france_2020_2026.csv` (version agrégée) | [ACLED Data Export Tool](https://acleddata.com), France, depuis 2020 |
| `sondages_1er_tour.csv`, `sondages_2nd_tour.csv` (sondages 2017, 2022 et 2027, tableaux Wikipédia) | [hugoC1/sondages_presidentielles](https://github.com/hugoC1/sondages_presidentielles/tree/main/data) |

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
notebooks/      notebook principal BOURKHIS_notebook.ipynb (fonctions + main)
dashboard/      application Dash
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancer le notebook puis le dashboard

1. Exécuter `notebooks/BOURKHIS_notebook.ipynb` en entier : il crée les fichiers de `data/processed/`.
2. Lancer le dashboard, puis ouvrir http://127.0.0.1:8050 :

```bash
python dashboard/app.py
```

Le dashboard a six onglets : carte et évolution par famille politique (2002-2022 et tendance 2027,
cliquer sur un département pour voir son historique), second tour 2027 par duel, abstention, lien entre le
vote 2022 et les indicateurs socio-économiques, groupes de départements (clustering spatial ou vote seul)
et règles d'association.

## Une seule table, des clés communes

Le notebook rassemble toutes les sources dans `data/processed/table_unique.parquet` : une ligne par département
et par tour (2002-2022, plus la tendance 2027), 35 colonnes. Les sources se relient par des clés communes :

| Source | Clé |
|---|---|
| Résultats (bureau de vote) | `code_departement`, `code_commune` (INSEE), `id_election` |
| Communes 2026 | `code_insee` → `dep_code`, région |
| Filosofi 2023 | code du département |
| Immigration 2022 (recensement) | code de la commune → département |
| ACLED | région + semaine (12 mois avant l'élection) |
| Indice des prix | mois de l'élection |
| Sondages | famille politique + année |
| Contours | code du département |

Les 96 départements de métropole trouvent une correspondance dans chaque source (les codes d'outre-mer diffèrent).

## Tendance 2027

**1er tour.** Pour chaque département et chaque famille politique, le notebook garde l'écart au score national
de 2022 et l'applique à une moyenne pondérée des sondages 2027 (les sondages récents comptent plus, demi-vie de
30 jours ; les hypothèses avec des candidats qui ont renoncé sont retirées). Un test sur le passé (prévoir 2017
et 2022 avec les élections d'avant, en connaissant le résultat national) montre que garder l'écart de 2022 se
trompe le moins : 1,2 point par département et par famille, contre 1,4 point en prolongeant la pente.

**Test complet.** On refait toute la méthode avec les seuls sondages disponibles à l'époque. À 5 mois du
1er tour (la situation d'aujourd'hui pour 2027), on se trompe de 4 à 6 points par département pour les grandes
familles (Mélenchon sous-estimé de 7 à 13 points, la droite surestimée de 8 points). À 1 mois, l'erreur tombe à
2 ou 3 points. L'extrême droite est la famille la plus stable dans les sondages.

**Second tour.** Score de Le Pen dans chaque duel (moyenne pondérée des sondages de ce duel) plus l'écart de
chaque département au national du second tour 2022. La carte, testée en prévoyant 2022 avec 2017, se trompe de
2 points et donne le bon gagnant dans 93 % des départements. Mais les sondages surestimaient Le Pen de 2 à
4 points au second tour en 2017 et 2022.

C'est une tendance, pas une prévision : l'incertitude principale reste le niveau national des sondages.

## Rendus

- `notebooks/BOURKHIS_notebook.ipynb` : le notebook.
- `docs/BOURKHIS_dashboard.html` : export statique du dashboard (preuve de fonctionnement).
- `docs/demo.md` : déroulé de la démo et questions probables.
