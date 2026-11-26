# Déroulé de la démo (environ 5 minutes)

La personne qui fait la démo est tirée au sort juste avant : chaque membre de l'équipe doit pouvoir la faire.

## Avant la séance
1. Les données brutes sont dans `data/raw/` (voir le README).
2. Le notebook `notebooks/BOURKHIS_notebook.ipynb` a été exécuté une fois en entier, pour que `data/processed/` existe.
3. Avoir le notebook ouvert et `docs/BOURKHIS_dashboard.html` prêt dans un onglet, au cas où le serveur Dash ne démarre pas.

## Pendant la démo
1. **En-tête et description** (30 s) : équipe, lien GitHub, les trois dimensions du dataset, le tableau des indicateurs.
2. **Exploration** (30 s) : lancer `main()`. Montrer pour une table le nombre de lignes et de colonnes, les types, les valeurs manquantes et les plages de valeurs.
3. **Requête 1** (45 s) : les quatre premiers de chaque élection, la courbe nationale des familles, l'abstention, puis le résultat contre-intuitif sur l'immigration (corrélation -0,37 avec l'extrême droite, +0,71 avec la gauche radicale).
4. **Requête 2** (45 s) : le tableau des règles. Lire la première règle et expliquer support, confiance, lift.
5. **Requête 3** (1 min) : la série des sondages 2027 et sa prévision ARIMA (onglet « Sondages 2027 »), le tableau qui compare les méthodes sur 2017 et 2022, puis le test de la carte (1,2 point d'erreur en gardant l'écart de 2022) et la carte 2027. Puis le test complet (à 5 mois, les sondages se trompaient beaucoup : Mélenchon 2022 annoncé à 11 %, il fait 24 %).
6. **Requête 4** (45 s) : le K-means sur le vote seul (silhouette 0,20, groupes éparpillés), puis le clustering spatial sur le vote et la position (silhouette 0,27, cohérence spatiale 0,81 contre 0,74) : la carte montre 6 grandes zones.
7. **Dashboard** (1 min) : `main()` le lance à la fin (lien http://127.0.0.1:8050).
   - Carte et évolution : extrême droite, glisser le curseur de 2002 à 2027*, cliquer sur un département.
   - Vote et territoires : niveau de vie médian, corrélation de -0,50.
   - Groupes de départements (vote + position, puis vote seul), puis Règles d'association.

## Questions probables
- **Pourquoi des familles politiques ?** Les candidats changent à chaque élection, et l'étiquette politique est vide en 2017 et 2022.
- **Pourquoi une tendance et pas une prévision ?** Le test sur le passé montre que la carte est fiable (environ 1 point d'erreur par département quand on connaît le résultat national), mais le niveau national vient des sondages, faits 5 mois avant l'élection.
- **Pourquoi ne pas prolonger la pente ?** On l'a testé : sur 2017 et 2022, prolonger la pente se trompe plus (1,4 point) que garder l'écart de 2022 (1,2 point). La géographie du vote bouge peu.
- **Où est la série temporelle ?** Dans les sondages : une série hebdomadaire par famille, prolongée jusqu'au vote par un ARIMA(0,1,1). Testé sur 2017 et 2022 avec les sondages de l'époque, il se trompe de 4,2 points sur le national, contre 5,3 pour la moyenne pondérée et 4,5 pour le dernier sondage. Sur les élections elles-mêmes, ARIMA n'a pas de sens : 5 points par série. C'est pour ça que la carte garde l'écart de 2022.
- **Pourquoi ARIMA plutôt que la moyenne des sondages ?** La moyenne pondérée (demi-vie de 30 jours) réagit en retard aux mouvements de l'opinion. Sur 2017 et 2022, ARIMA(0,1,1) se trompe d'un point de moins en moyenne. Le gain reste modeste : on ne l'a testé que sur 2 élections.
- **Pourquoi la silhouette est-elle basse (0,20 et 0,27) ?** Les départements forment un continuum ; les groupes sont réels mais se chevauchent.
- **L'immigration explique-t-elle le vote d'extrême droite ?** Pas au niveau des départements : la corrélation est négative (-0,37) et nulle hors Île-de-France et Méditerranée. Le Pas-de-Calais et l'Aisne votent très à l'extrême droite avec 3 à 5 % d'immigrés. Ajoutée au revenu et à la pauvreté, elle améliore pourtant le modèle (R² de 0,50 à 0,57). On compare des départements, pas des personnes.
- **Et l'âge, le chômage ?** Ajoutés depuis l'INSEE, pour l'année de chaque élection. Des deux, c'est le chômage qui pèse sur l'extrême droite (+3,3 points par écart-type, corrélation +0,41) : R² de 0,56 à 0,61. L'âge compte surtout pour l'abstention (plus de 60 ans et plus, moins d'abstention) : R² de 0,52 à 0,58. Seule, la part des 60 ans et plus suit l'extrême droite (+0,30), mais elle n'ajoute presque rien une fois la ruralité prise en compte. La part des 20-39 ans reste hors du modèle : corrélée à -0,91 avec celle des 60 ans et plus.
- **Et le diplôme, les CSP ?** On a testé trois modèles : diplôme, CSP, les deux. Le diplôme gagne : R² de l'extrême droite de 0,61 à 0,77 (0,73 avec les CSP), abstention de 0,58 à 0,78. La part des bac+3 est le facteur le plus fort du modèle (-6,4 points par écart-type). Les deux ensemble n'apportent rien : bac+3 et cadres sont corrélés à 0,97. Avec 12 indicateurs pour 96 départements, le R² est optimiste ; en validation croisée il est plus bas, mais le diplôme reste ce qui l'améliore le plus.
- **Pourquoi ACLED par région ?** L'accès gratuit ne donne que la version agrégée ; la version complète est demandée.
- **Que fait `LANCER_DASHBOARD=0` ?** Il permet d'exécuter le notebook sans lancer le serveur (tests).
- **Qui va gagner en 2027 ?** Hors projet (annexe, curiosité personnelle) : Le Pen est en tête dans tous les sondages de second tour (55 % contre Philippe), mais les sondages la surestimaient de 2 à 4 points en 2017 et 2022, et à 5 mois du vote ils se trompaient beaucoup au 1er tour. Contre Philippe, le duel reste ouvert.
- **Les chiffres nationaux viennent d'où ?** De la somme de la table unique, donc de la métropole seule. Les parts des familles sont à quelques dixièmes des chiffres officiels ; l'abstention est 2 points plus basse, car l'outre-mer et l'étranger votent moins.
- **Comment les sources sont-elles reliées ?** Par des clés communes : code du département, code INSEE de la commune, région, date de l'élection, famille politique. La table unique (`table_unique.parquet`) les rassemble, et `verifier_cles` montre que les 96 départements de métropole sont trouvés dans chaque source.
- **Pourquoi deux clustering ?** Le premier regroupe les départements qui votent pareil, où qu'ils soient. Le second, spatial, ajoute la position : il donne des zones d'un seul tenant, ce qu'on attend d'un clustering spatial.
