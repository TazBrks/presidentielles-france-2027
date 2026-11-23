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

Les données brutes ne sont pas versionnées : les placer dans `data/raw/`.

## Structure

```
data/
  raw/          données brutes (non versionnées)
  processed/    données nettoyées
notebooks/      notebook principal (fonctions + main)
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
