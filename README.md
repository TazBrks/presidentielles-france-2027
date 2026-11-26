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
- INSEE, recensement 2022 : immigration par commune
- INSEE : population par grande classe d'âge et taux de chômage localisé, par département et par année
- Sondages 2017-2027 (tableaux Wikipédia, dépôt hugoC1/sondages_presidentielles)

## Récupérer les données

Les données brutes sont versionnées dans `data/raw/` : un `git clone` suffit pour exécuter le notebook.
Deux exceptions :

- `general_results.parquet` et `candidats_results.parquet` sont des **extraits** des fichiers de data.gouv.fr,
  limités aux 10 tours de présidentielle 2002-2022 (le fichier complet des candidats fait 161 Mo, au-delà de la
  limite de 100 Mo de GitHub). Les colonnes sont identiques : le notebook fonctionne aussi avec les fichiers complets.
- `acled_france_2020_2026.csv` (l'export ACLED complet) n'est pas versionné. À sa place, `data/reference/acled_agrege_region_semaine.csv`
  contient le nombre d'événements par semaine, région et type : c'est tout ce que le notebook utilise, et il le lit
  automatiquement quand l'export manque. Avec l'export dans `data/raw/`, le notebook le préfère.

Les sources de chaque fichier :

| Fichier | Source |
|---|---|
| `general_results.parquet` | [data.gouv.fr, Données des élections agrégées](https://www.data.gouv.fr/datasets/donnees-des-elections-agregees) |
| `candidats_results.parquet` | même page |
| 8 CSV des sondages 2027 (`sondages-presidentielle-2027.csv`, `projection-departementale-1er-tour.csv`, etc.) | [data.gouv.fr, Présidentielle 2027 : sondages, candidatures et projection départementale](https://www.data.gouv.fr/datasets/presidentielle-2027-sondages-candidatures-et-projection-departementale) |
| `sondages.json` (29 sondages 2027, toutes hypothèses) | data.gouv.fr, sondages d'intentions de vote 2027 |
| `communes-france-2026.parquet` | [data.gouv.fr, liste des communes de France](https://www.data.gouv.fr/datasets/6745d9ae4524d845d2138193) |
| `FILOSOFI_CC_csv.zip` | [INSEE, Filosofi 2023](https://www.insee.fr/fr/statistiques/8984752) |
| `TD_IMG1A_2022_csv.zip` (facultatif : déjà agrégé dans `data/reference/immigres_departements_2022.csv`) | [INSEE, recensement 2022, immigration](https://www.insee.fr/fr/statistiques/8582054?sommaire=8582058) |
| `estim-pop-dep-sexe-gca-1975-2023.xls` (population par âge, chaque 1er janvier) | [INSEE, estimations de population](https://www.insee.fr/fr/statistiques/1893198) |
| `sl_etc_2026T2.xls` (taux de chômage localisé, trimestriel depuis 1982) | [INSEE, taux de chômage localisés](https://www.insee.fr/fr/statistiques/2012804) |
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
  raw/          données brutes (versionnées, sauf ACLED)
  processed/    données nettoyées (générées par le notebook, versionnées) ;
                table_unique.parquet / .csv : la table de travail qui réunit toutes les sources
  reference/    tables de référence (familles politiques)
notebooks/      notebook principal BOURKHIS_notebook.ipynb (fonctions + main)
dashboard/      application Dash
docs/           slides, export du dashboard, déroulé de la démo
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancer le notebook puis le dashboard

1. Exécuter `notebooks/BOURKHIS_notebook.ipynb` en entier : il crée les fichiers de `data/processed/` (environ 20 s).
   Les fichiers de `data/processed/` sont déjà versionnés : on peut lancer le dashboard sans exécuter le notebook.
2. Lancer le dashboard, puis ouvrir http://127.0.0.1:8050 :

```bash
python dashboard/app.py
```

Le dashboard a six onglets : carte et évolution par famille politique (2002-2022 et tendance 2027,
cliquer sur un département pour voir son historique), abstention, lien entre le
vote 2022 et les indicateurs socio-économiques, groupes de départements (clustering spatial ou vote seul)
règles d'association, et un onglet bonus hors projet (second tour 2027).

## Une seule table, des clés communes

Le notebook rassemble toutes les sources dans `data/processed/table_unique.parquet` : une ligne par département
et par tour (2002-2022, plus la tendance 2027), 48 colonnes. Les sources se relient par des clés communes :

| Source | Clé |
|---|---|
| Résultats (bureau de vote) | `code_departement`, `code_commune` (INSEE), `id_election` |
| Communes 2026 | `code_insee` → `dep_code`, région |
| Filosofi 2023 | code du département |
| Immigration 2022 (recensement) | code de la commune → département |
| Âge et chômage (INSEE) | code du département + année de l'élection |
| ACLED | région + semaine (12 mois avant l'élection) |
| Indice des prix | mois de l'élection |
| Sondages | famille politique + année |
| Contours | code du département |

Les 96 départements de métropole trouvent une correspondance dans chaque source (les codes d'outre-mer diffèrent).

C'est la **seule table de travail** : toutes les requêtes la lisent, et les chiffres nationaux sont la somme de ses lignes
(métropole : l'abstention y est environ 2 points plus basse que le chiffre officiel France entière). Elle contient aussi
le sondage national de l'époque pour chaque famille (`sondage_<famille>`, 2017, 2022 et 2027).

## Tendance 2027

**Niveau national : série temporelle des sondages.** Les sondages 2027 forment une série hebdomadaire par famille,
prolongée jusqu'au 1er tour par un modèle **ARIMA(0,1,1)**. Le modèle a été choisi par un test sur 2017 et 2022
(prévoir le résultat national avec les seuls sondages publiés 5 mois ou 1 mois avant le vote) parmi six méthodes :

| Méthode | Erreur moyenne (points) |
|---|---|
| ARIMA(0,1,1) (retenue) | 4,2 |
| ARIMA(1,1,0) | 4,2 |
| Holt (tendance amortie) | 4,3 |
| Dernier sondage | 4,5 |
| Lissage exponentiel simple | 4,5 |
| Moyenne pondérée (demi-vie 30 jours) | 5,3 |

**Carte.** Pour chaque département et chaque famille, le notebook garde l'écart au score national de 2022 et
l'applique au niveau national prévu. Un test sur le passé (prévoir 2017 et 2022 avec les élections d'avant, en
connaissant le résultat national) montre que garder l'écart de 2022 se trompe le moins : 1,2 point par département
et par famille, contre 1,4 point en prolongeant la pente. Avec 5 élections par série, un ARIMA n'aurait pas de sens.

**Test complet.** On refait toute la méthode avec les seuls sondages disponibles à l'époque. À 5 mois du
1er tour (la situation d'aujourd'hui pour 2027), on se trompe de 4 à 6 points par département pour les grandes
familles (Mélenchon sous-estimé de 7 à 13 points, la droite surestimée de 8 points). À 1 mois, l'erreur tombe à
2 ou 3 points. L'extrême droite est la famille la plus stable dans les sondages.

**Bonus, hors projet : le second tour.** En annexe du notebook (curiosité personnelle, autre source : les sondages
de second tour), le score de Le Pen dans chaque duel plus l'écart de chaque département au second tour 2022.

C'est une tendance, pas une prévision : l'incertitude principale reste le niveau national des sondages.

## Rendus

- `notebooks/BOURKHIS_notebook.ipynb` : le notebook.
- `docs/BOURKHIS_dashboard.html` : export statique du dashboard (preuve de fonctionnement).
- `docs/BOURKHIS_slides.pdf` : les slides de la soutenance (format demandé par le sujet).
- `docs/BOURKHIS_slides.pptx` : les mêmes slides en PowerPoint modifiable, avec les notes de l'oral (polices Dela Gothic One et Trispace, sur Google Fonts).
- `docs/demo.md` : déroulé de la démo et questions probables.
