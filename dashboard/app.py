"""Dashboard Dash : présidentielles françaises 2002-2022 et tendance 2027.

Lancer d'abord le notebook (notebooks/BOURKHIS_notebook.ipynb), qui crée les fichiers de data/processed,
puis : python dashboard/app.py
"""
from pathlib import Path
import json

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dash_table, dcc, html

EQUIPE = ['Manel HASSAN', "Tasnim BOURKHIS (cheffe d'équipe)", 'Julia PLAYE-LORENTE', 'Marie BARDET', 'Inès BENBARA', 'Karell Steve JODOM CHOUDJA']
DATASET = "Données des élections agrégées (data.gouv.fr), présidentielles 2002-2022"

DOSSIER = Path(__file__).resolve().parent.parent / "data"
PROCESSED = DOSSIER / "processed"

FAMILLES = {
    "extreme_gauche": "Extrême gauche", "gauche_radicale": "Gauche radicale", "gauche": "Gauche",
    "ecologistes": "Écologistes", "centre": "Centre", "droite": "Droite",
    "souverainistes": "Souverainistes", "extreme_droite": "Extrême droite", "divers": "Divers",
}
INDICATEURS = {
    "niveau_vie_median": "Niveau de vie médian (€)", "taux_pauvrete": "Taux de pauvreté (%)",
    "part_immigres": "Part d'immigrés",
    "indice_gini": "Indice de Gini", "part_revenu_chomage": "Part du chômage dans le revenu (%)",
    "densite": "Densité (hab./km²)", "part_population_rurale": "Part de population rurale",
    "manifestations_pour_100k": "Manifestations ACLED pour 100 000 hab. (région)",
    "taux_chomage": "Taux de chômage (%)", "part_20_39_ans": "Part des 20-39 ans",
    "part_60_ans_et_plus": "Part des 60 ans et plus",
}


# Fonction qui charge les fichiers produits par le notebook
# Entrée : aucune (lit la table unique et les résultats des requêtes dans data/processed, et les contours)
# Sortie : contours (GeoJSON), noms des départements, puis les DataFrames votes, participation, évolution
#          nationale, départements 2022, règles, série des sondages 2027, test des séries temporelles,
#          et pour l'onglet bonus le second tour 2027 et les duels
def charger_donnees():
    """Charge les fichiers produits par le notebook."""
    with open(DOSSIER / "reference" / "departements.geojson", encoding="utf-8") as f:
        contours = json.load(f)
    noms = {f["properties"]["code"]: f["properties"]["nom"] for f in contours["features"]}
    # La table unique (une ligne par département et par tour, 2027 = tendance) alimente les cartes du vote
    # et de l'abstention
    table = pd.read_parquet(PROCESSED / "table_unique.parquet")
    table = table[table["code_departement"].isin(noms)]
    premier_tour = table[table["tour"] == 1]
    votes = premier_tour.melt(id_vars=["code_departement", "annee"],
                              value_vars=[c for c in table.columns if c.startswith("vote_")],
                              var_name="famille", value_name="part_exprimes")
    votes["famille"] = votes["famille"].str.removeprefix("vote_")
    votes["departement"] = votes["code_departement"].map(noms)
    participation = table[~table["est_tendance"]]
    evolution = pd.read_parquet(PROCESSED / "evolution_nationale.parquet")
    departements = pd.read_parquet(PROCESSED / "departements_2022.parquet")
    departements["departement"] = departements["code_departement"].map(noms)
    regles = pd.read_parquet(PROCESSED / "regles_association.parquet")
    second_tour = pd.read_parquet(PROCESSED / "second_tour_2027.parquet")
    second_tour = second_tour[second_tour["code_departement"].isin(noms)]
    second_tour["departement"] = second_tour["code_departement"].map(noms)
    duels = pd.read_parquet(PROCESSED / "duels_2027.parquet")
    serie = pd.read_parquet(PROCESSED / "serie_sondages_2027.parquet")
    tests = pd.read_parquet(PROCESSED / "test_series_temporelles.parquet")
    return contours, noms, votes, participation, evolution, departements, regles, second_tour, duels, serie, tests


(CONTOURS, NOMS, VOTES, PARTICIPATION, EVOLUTION, DEPARTEMENTS, REGLES,
 SECOND_TOUR, DUELS, SERIE_2027, TESTS_SERIES) = charger_donnees()
ANNEES = sorted(VOTES["annee"].unique())


# Fonction qui dessine la carte des groupes de départements
# Entrée : colonne du découpage ("nom_cluster" ou "nom_cluster_spatial")
# Sortie : figure Plotly (carte)
def figure_clusters(colonne="nom_cluster"):
    fig = px.choropleth(DEPARTEMENTS, geojson=CONTOURS, locations="code_departement",
                        featureidkey="properties.code", color=colonne, hover_name="departement",
                        category_orders={colonne: sorted(DEPARTEMENTS[colonne].unique())})
    fig.update_geos(fitbounds="locations", visible=False)
    titre = "Groupes de départements (vote seul)" if colonne == "nom_cluster" else "Clustering spatial (vote + position)"
    fig.update_layout(title=titre, margin=dict(l=0, r=0, t=40, b=0),
                      legend=dict(orientation="h", y=-0.05, title=None))
    return fig


# Fonction qui trace la série hebdomadaire des sondages 2027 et la prévision ARIMA au jour du 1er tour
# Entrée : aucune (SERIE_2027 : semaines de sondages puis un point « prévision » par famille)
# Sortie : figure Plotly (courbes en trait plein, prévision en pointillés)
def figure_serie_2027(familles=("extreme_droite", "gauche_radicale", "centre", "droite", "gauche")):
    df = SERIE_2027[SERIE_2027["famille"].isin(familles)].copy()
    df["famille"] = df["famille"].map(FAMILLES)
    fig = px.line(df[df["type"] == "sondages"], x="semaine", y="part", color="famille",
                  title="Sondages 2027 par famille (série hebdomadaire) et prévision au 1er tour (pointillés)")
    for trace in list(fig.data):
        f = df[df["famille"] == trace.name].sort_values("semaine")
        fig.add_scatter(x=f["semaine"].iloc[-2:], y=f["part"].iloc[-2:], mode="lines+markers", showlegend=False,
                        line={"dash": "dot", "color": trace.line.color})
    fig.update_yaxes(tickformat=".0%", title="Part des intentions")
    fig.update_xaxes(title=None)
    fig.update_layout(legend={"orientation": "h", "y": -0.12, "title": None})
    return fig


# Fonction qui compare le profil de vote moyen de chaque groupe
# Entrée : colonne du découpage
# Sortie : figure Plotly (barres groupées)
def figure_profils(colonne="nom_cluster"):
    colonnes = [c for c in DEPARTEMENTS.columns if c.startswith("vote_") and c != "vote_divers"] + ["taux_abstention"]
    profils = DEPARTEMENTS.groupby(colonne)[colonnes].mean().reset_index().melt(
        id_vars=colonne, var_name="indicateur", value_name="part")
    profils["indicateur"] = profils["indicateur"].map(
        lambda c: "Abstention" if c == "taux_abstention" else FAMILLES[c.replace("vote_", "")])
    fig = px.bar(profils, x="indicateur", y="part", color=colonne, barmode="group",
                 category_orders={colonne: sorted(DEPARTEMENTS[colonne].unique())},
                 title="Profil moyen de chaque groupe (1er tour 2022)")
    fig.update_yaxes(tickformat=".0%", title=None)
    fig.update_layout(xaxis_title=None, legend=dict(orientation="h", y=-0.25, title=None))
    return fig

app = Dash(__name__, title="Présidentielles 2002-2027")

app.layout = html.Div(style={"fontFamily": "sans-serif", "maxWidth": "1200px", "margin": "auto"}, children=[
    html.H1("Présidentielles françaises : 2002-2022 et tendance 2027"),
    html.P([html.B("Équipe : "), ", ".join(EQUIPE), html.Br(), html.B("Dataset : "), DATASET]),
    html.P("Résultats du 1er tour par département (data.gouv.fr). 2027 : tendance construite à partir des "
           "écarts au national de 2022 et d'une moyenne pondérée des sondages (les récents comptent plus). C'est une tendance, pas une prévision (2027* sur le curseur)."),
    dcc.Tabs([
        dcc.Tab(label="Carte et évolution", children=[
            html.Div(style={"display": "flex", "gap": "20px", "margin": "15px 0"}, children=[
                html.Div([html.Label("Famille politique"),
                          dcc.Dropdown(id="famille", value="extreme_droite", clearable=False,
                                       options=[{"label": v, "value": k} for k, v in FAMILLES.items()])],
                         style={"width": "300px"}),
                html.Div([html.Label("Élection"),
                          dcc.Slider(id="annee", min=ANNEES[0], max=ANNEES[-1], step=None, value=2022,
                                     marks={int(a): ("2027*" if a == 2027 else str(a)) for a in ANNEES})],
                         style={"flex": 1, "paddingRight": "40px"}),
            ]),
            html.Div(style={"display": "flex"}, children=[
                dcc.Graph(id="carte", style={"flex": 1, "height": "600px"}),
                dcc.Graph(id="evolution-departement", style={"flex": 1, "height": "600px"}),
            ]),
            dcc.Graph(id="evolution-nationale"),
        ]),
        dcc.Tab(label="Sondages 2027 (série temporelle)", children=[
            html.P("Le niveau national 2027 vient de la série hebdomadaire des sondages, prolongée jusqu'au 1er tour "
                   "par un modèle ARIMA(0,1,1). La méthode a été choisie par un test sur 2017 et 2022 : on prévoit le "
                   "résultat national avec les seuls sondages publiés 5 mois ou 1 mois avant le vote.",
                   style={"margin": "15px 0"}),
            dcc.Graph(figure=figure_serie_2027(), style={"height": "550px"}),
            html.B("Erreur moyenne sur le résultat national (points), selon la méthode"),
            dash_table.DataTable(
                data=TESTS_SERIES.pivot_table(index="methode", values="erreur_moyenne_points", columns="fenetre")
                .assign(moyenne=lambda t: t.mean(axis=1)).sort_values("moyenne").round(2).reset_index()
                .to_dict("records"),
                columns=[{"name": n, "id": c} for c, n in [("methode", "Méthode"), ("5 mois avant", "5 mois avant"),
                                                          ("1 mois avant", "1 mois avant"), ("moyenne", "Moyenne")]],
                style_cell={"fontFamily": "sans-serif", "padding": "6px", "textAlign": "left"},
                style_header={"fontWeight": "bold"}),
        ]),
        dcc.Tab(label="Abstention", children=[
            html.Div(style={"width": "300px", "margin": "15px 0"}, children=[
                html.Label("Élection"),
                dcc.Dropdown(id="election-abstention", clearable=False, value="2022_pres_t1",
                             options=sorted(PARTICIPATION["id_election"].unique()))]),
            dcc.Graph(id="carte-abstention", style={"height": "600px"}),
        ]),
        dcc.Tab(label="Vote et territoires (2022)", children=[
            html.Div(style={"display": "flex", "gap": "20px", "margin": "15px 0"}, children=[
                html.Div([html.Label("Indicateur"),
                          dcc.Dropdown(id="indicateur", value="niveau_vie_median", clearable=False,
                                       options=[{"label": v, "value": k} for k, v in INDICATEURS.items()])],
                         style={"width": "400px"}),
                html.Div([html.Label("Vote (1er tour 2022)"),
                          dcc.Dropdown(id="famille-nuage", value="extreme_droite", clearable=False,
                                       options=[{"label": v, "value": k} for k, v in FAMILLES.items()
                                                if f"vote_{k}" in DEPARTEMENTS])],
                         style={"width": "300px"}),
            ]),
            dcc.Graph(id="nuage", style={"height": "600px"}),
        ]),
        dcc.Tab(label="Groupes de départements", children=[
            html.P("K-means sur le profil de vote au 1er tour 2022 (part de chaque famille et abstention). "
                   "Le clustering spatial ajoute la position du département (latitude, longitude), qui pèse autant que "
                   "le vote : les groupes forment des zones d'un seul tenant. Le nombre de groupes est choisi par le "
                   "score de silhouette.", style={"margin": "15px 0"}),
            html.Div(style={"width": "300px", "marginBottom": "10px"}, children=[
                html.Label("Découpage"),
                dcc.Dropdown(id="decoupage", value="nom_cluster_spatial", clearable=False,
                             options=[{"label": "Vote + position (spatial)", "value": "nom_cluster_spatial"},
                                      {"label": "Vote seul", "value": "nom_cluster"}])]),
            html.Div(style={"display": "flex"}, children=[
                dcc.Graph(id="carte-clusters", style={"flex": 1, "height": "600px"}),
                dcc.Graph(id="profil-clusters", style={"flex": 1, "height": "600px"}),
            ]),
        ]),
        dcc.Tab(label="Règles d'association", children=[
            html.P("Apriori sur les profils des départements (au-dessus ou au-dessous de la médiane). "
                   "Support : part des départements concernés. Confiance : part des départements qui ont les "
                   "antécédents et aussi la conséquence. Lift > 1 : la règle est plus fréquente que le hasard.",
                   style={"margin": "15px 0"}),
            dash_table.DataTable(
                data=REGLES.round(2).to_dict("records"),
                columns=[{"name": n, "id": c} for c, n in [("antecedents", "Si le département est..."),
                                                          ("consequents", "alors il a souvent..."),
                                                          ("support", "Support"), ("confidence", "Confiance"),
                                                          ("lift", "Lift")]],
                style_cell={"fontFamily": "sans-serif", "padding": "8px", "textAlign": "left"},
                style_header={"fontWeight": "bold"}),
        ]),
        dcc.Tab(label="Bonus : second tour 2027 (hors projet)", children=[
            html.P("Curiosité personnelle, hors du projet (autre source : les sondages de second tour). Score de Le Pen par département dans chaque duel : moyenne pondérée des sondages de ce duel, "
                   "plus l'écart de chaque département au national du second tour 2022. Attention : en 2017 et 2022, "
                   "les sondages surestimaient Le Pen de 2 à 4 points au second tour.", style={"margin": "15px 0"}),
            html.Div(style={"width": "300px", "marginBottom": "10px"}, children=[
                html.Label("Adversaire de Le Pen"),
                dcc.Dropdown(id="adversaire", value="Philippe", clearable=False,
                             options=sorted(SECOND_TOUR["adversaire"].unique()))]),
            html.Div(style={"display": "flex"}, children=[
                dcc.Graph(id="carte-second-tour", style={"flex": 2, "height": "600px"}),
                html.Div(style={"flex": 1, "paddingTop": "40px"}, children=[
                    html.B("Moyenne des sondages par duel (score de Le Pen, %)"),
                    dash_table.DataTable(
                        data=DUELS.round(1).astype({"dernier_sondage": str}).to_dict("records"),
                        columns=[{"name": n, "id": c} for c, n in [("adversaire", "Adversaire"),
                                                                  ("nb_sondages", "Sondages"),
                                                                  ("score_rn", "Le Pen"), ("min", "Min"),
                                                                  ("max", "Max")]],
                        style_cell={"fontFamily": "sans-serif", "padding": "6px", "textAlign": "left"},
                        style_header={"fontWeight": "bold"}),
                ]),
            ]),
        ]),
    ]),
])


# Fonction qui dessine une carte des départements colorée selon une colonne
# Entrée : DataFrame avec code_departement, colonne à colorer, titre, libellé de la légende
# Sortie : figure Plotly (carte)
def carte(df, colonne, titre, etiquette):
    fig = px.choropleth(df, geojson=CONTOURS, locations="code_departement", featureidkey="properties.code",
                        color=colonne, hover_name="departement", color_continuous_scale="Viridis",
                        labels={colonne: etiquette})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title=titre, margin=dict(l=0, r=0, t=40, b=0))
    return fig


# Fonction qui met à jour la carte d'une famille pour une élection (callback)
# Entrée : famille choisie, année choisie (2027 = tendance)
# Sortie : figure Plotly (carte)
@app.callback(Output("carte", "figure"), Input("famille", "value"), Input("annee", "value"))
def maj_carte(famille, annee):
    df = VOTES[(VOTES["famille"] == famille) & (VOTES["annee"] == annee)]
    titre = f"{FAMILLES[famille]} au 1er tour {annee}" + (" (tendance)" if annee == 2027 else "")
    fig = carte(df, "part_exprimes", titre, "Part des exprimés")
    fig.update_coloraxes(colorbar_tickformat=".0%")
    return fig


# Fonction qui trace l'historique d'une famille dans le département cliqué (callback)
# Entrée : famille choisie, clic sur la carte (Paris par défaut)
# Sortie : figure Plotly (courbe)
@app.callback(Output("evolution-departement", "figure"), Input("famille", "value"), Input("carte", "clickData"))
def maj_departement(famille, clic):
    code = clic["points"][0]["location"] if clic else "75"
    df = VOTES[VOTES["code_departement"] == code].copy()
    df["famille"] = df["famille"].map(FAMILLES)
    fig = px.line(df.sort_values("annee"), x="annee", y="part_exprimes", color="famille", markers=True,
                  title=f"{NOMS[code]} ({code}) : toutes les familles (cliquer sur la carte pour changer)")
    fig.update_traces(opacity=0.35)
    fig.update_traces(opacity=1, line_width=4, selector={"name": FAMILLES[famille]})
    fig.add_vline(x=2024.5, line_dash="dot")
    fig.update_yaxes(tickformat=".0%", title="Part des exprimés")
    fig.update_xaxes(title="Année")
    return fig


# Fonction qui trace l'évolution nationale des familles, la famille choisie en avant (callback)
# Entrée : famille choisie
# Sortie : figure Plotly (courbes)
@app.callback(Output("evolution-nationale", "figure"), Input("famille", "value"))
def maj_nationale(famille):
    df = EVOLUTION.reset_index().melt(id_vars="annee", var_name="famille", value_name="part")
    df["famille"] = df["famille"].map(FAMILLES)
    fig = px.line(df, x="annee", y="part", color="famille", markers=True,
                  title="France : part des exprimés au 1er tour (2027 : moyenne des sondages)")
    fig.update_traces(opacity=0.35)
    fig.update_traces(opacity=1, line_width=4, selector={"name": FAMILLES[famille]})
    fig.add_vline(x=2024.5, line_dash="dot")
    fig.update_yaxes(tickformat=".0%", title="Part des exprimés")
    fig.update_xaxes(title="Année")
    return fig


# Fonction qui met à jour la carte de l'abstention (callback)
# Entrée : identifiant de l'élection (ex. "2022_pres_t1")
# Sortie : figure Plotly (carte)
@app.callback(Output("carte-abstention", "figure"), Input("election-abstention", "value"))
def maj_abstention(election):
    df = PARTICIPATION[PARTICIPATION["id_election"] == election].copy()
    df["departement"] = df["code_departement"].map(NOMS)
    fig = carte(df, "taux_abstention", f"Abstention : {election}", "Abstention")
    fig.update_coloraxes(colorbar_tickformat=".0%")
    return fig


# Fonction qui croise le vote 2022 d'une famille avec un indicateur, avec la corrélation (callback)
# Entrée : nom de l'indicateur, famille
# Sortie : figure Plotly (nuage de points avec droite de tendance)
@app.callback(Output("nuage", "figure"), Input("indicateur", "value"), Input("famille-nuage", "value"))
def maj_nuage(indicateur, famille):
    fig = px.scatter(DEPARTEMENTS, x=indicateur, y=f"vote_{famille}", hover_name="departement",
                     trendline="ols" if _statsmodels_disponible() else None,
                     labels={indicateur: INDICATEURS[indicateur], f"vote_{famille}": f"{FAMILLES[famille]} (2022)"},
                     title=f"{FAMILLES[famille]} et {INDICATEURS[indicateur].lower()}, par département")
    correlation = DEPARTEMENTS[indicateur].corr(DEPARTEMENTS[f"vote_{famille}"])
    fig.add_annotation(text=f"Corrélation : {correlation:.2f}", xref="paper", yref="paper", x=0.01, y=0.99,
                       showarrow=False)
    fig.update_yaxes(tickformat=".0%")
    return fig


# Fonction qui met à jour la carte du second tour 2027 pour un duel (callback)
# Entrée : nom de l'adversaire de Le Pen
# Sortie : figure Plotly (carte du score de Le Pen)
@app.callback(Output("carte-second-tour", "figure"), Input("adversaire", "value"))
def maj_second_tour(adversaire):
    df = SECOND_TOUR[SECOND_TOUR["adversaire"] == adversaire]
    fig = px.choropleth(df, geojson=CONTOURS, locations="code_departement", featureidkey="properties.code",
                        color="part_rn", hover_name="departement", range_color=(0.2, 0.8),
                        color_continuous_scale=[[0, "#1f5fa8"], [0.5, "#f7f7f7"], [1, "#2b0f4a"]],
                        labels={"part_rn": "Le Pen"})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_coloraxes(colorbar_tickformat=".0%")
    gagnes = int((df["part_rn"] > 0.5).sum())
    fig.update_layout(title=f"Le Pen contre {adversaire} : Le Pen en tête dans {gagnes} départements sur {len(df)}",
                      margin=dict(l=0, r=0, t=40, b=0))
    return fig


# Fonction qui change de découpage dans l'onglet des groupes (callback)
# Entrée : colonne du découpage
# Sortie : deux figures Plotly (carte, profils)
@app.callback(Output("carte-clusters", "figure"), Output("profil-clusters", "figure"), Input("decoupage", "value"))
def maj_clusters(colonne):
    return figure_clusters(colonne), figure_profils(colonne)


# Fonction qui vérifie si statsmodels est installé (droite de tendance du nuage de points)
# Entrée : aucune
# Sortie : booléen
def _statsmodels_disponible():
    try:
        import statsmodels  # noqa: F401
        return True
    except ImportError:
        return False


# Fonction qui renvoie l'application Dash
# Entrée : aucune
# Sortie : objet Dash (utilisé par main() dans le notebook)
def creer_app():
    """Renvoie l'application Dash (utilisé par main() dans le notebook)."""
    return app


if __name__ == "__main__":
    # threaded=False : plotly n'aime pas créer plusieurs figures en même temps dans des threads différents.
    app.run(debug=False, threaded=False)
