# Déroulé de la démo (environ 5 minutes)

La personne qui fait la démo est tirée au sort juste avant : chaque membre de l'équipe doit pouvoir la faire.

## Avant la séance
1. Les données brutes sont dans `data/raw/` (voir le README).
2. Le notebook `notebooks/BOURKHIS_notebook.ipynb` a été exécuté une fois en entier, pour que `data/processed/` existe.
3. Avoir le notebook ouvert et `docs/BOURKHIS_dashboard.html` prêt dans un onglet, au cas où le serveur Dash ne démarre pas.

## Pendant la démo
1. **En-tête et description** (30 s) : équipe, lien GitHub, les trois dimensions du dataset, le tableau des indicateurs.
2. **Exploration** (30 s) : lancer `main()`. Montrer pour une table le nombre de lignes et de colonnes, les types, les valeurs manquantes et les plages de valeurs.
3. **Requête 1** (45 s) : les quatre premiers de chaque élection, la courbe nationale des familles, l'abstention.
4. **Requête 2** (45 s) : le tableau des règles. Lire la première règle et expliquer support, confiance, lift.
5. **Requête 3** (45 s) : la moyenne des sondages par famille, la comparaison avec la projection du site (corrélation 0,97 à 0,99), la carte 2027.
6. **Requête 4** (45 s) : les scores de silhouette (3 groupes), le profil des groupes, la carte.
7. **Dashboard** (1 min) : `main()` le lance à la fin (lien http://127.0.0.1:8050).
   - Carte et évolution : extrême droite, glisser le curseur de 2002 à 2027*, cliquer sur un département.
   - Vote et territoires : niveau de vie médian, corrélation de -0,50.
   - Groupes de départements, puis Règles d'association.

## Questions probables
- **Pourquoi des familles politiques ?** Les candidats changent à chaque élection, et l'étiquette politique est vide en 2017 et 2022.
- **Pourquoi une tendance et pas une prévision ?** Cinq élections, c'est peu : on prolonge l'écart de chaque département au national et on le recale sur les sondages.
- **Pourquoi la silhouette est-elle basse (0,20) ?** Les départements forment un continuum ; les groupes sont réels mais se chevauchent.
- **Pourquoi ACLED par région ?** L'accès gratuit ne donne que la version agrégée ; la version complète est demandée.
- **Que fait `LANCER_DASHBOARD=0` ?** Il permet d'exécuter le notebook sans lancer le serveur (tests).
