"""Dashboard Dash : présidentielles françaises 2002-2022 et tendance 2027.

Lancer d'abord le notebook (notebooks/presidentielles.ipynb), qui crée les fichiers de data/processed,
puis : python dashboard/app.py
"""
from pathlib import Path
import json

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

DOSSIER = Path(__file__).resolve().parent.parent / "data"
PROCESSED = DOSSIER / "processed"

FAMILLES = {
    "extreme_gauche": "Extrême gauche", "gauche_radicale": "Gauche radicale", "gauche": "Gauche",
    "ecologistes": "Écologistes", "centre": "Centre", "droite": "Droite",
    "souverainistes": "Souverainistes", "extreme_droite": "Extrême droite", "divers": "Divers",
}
INDICATEURS = {
    "niveau_vie_median": "Niveau de vie médian (€)", "taux_pauvrete": "Taux de pauvreté (%)",
    "indice_gini": "Indice de Gini", "part_revenu_chomage": "Part du chômage dans le revenu (%)",
    "densite": "Densité (hab./km²)", "part_population_rurale": "Part de population rurale",
    "evenements_protests_pour_100k": "Manifestations ACLED pour 100 000 hab. (région)",
}


def charger_donnees():
    """Charge les fichiers produits par le notebook."""
    with open(DOSSIER / "reference" / "departements.geojson", encoding="utf-8") as f:
        contours = json.load(f)
    noms = {f["properties"]["code"]: f["properties"]["nom"] for f in contours["features"]}
    familles = pd.read_parquet(PROCESSED / "familles_departements.parquet")
    familles = familles[(familles["tour"] == 1) & familles["code_departement"].isin(noms)]
    tendance = pd.read_parquet(PROCESSED / "tendance_2027_departements.parquet")
    tendance = tendance[tendance["code_departement"].isin(noms)]
    # Une seule table : département x famille x année (2027 = tendance).
    votes = pd.concat([
        familles[["code_departement", "famille", "annee", "part_exprimes"]],
        tendance.assign(annee=2027).rename(columns={"part_2027": "part_exprimes"})[
            ["code_departement", "famille", "annee", "part_exprimes"]],
    ])
    votes["departement"] = votes["code_departement"].map(noms)
    participation = pd.read_parquet(PROCESSED / "participation_departements.parquet")
    participation = participation[participation["code_departement"].isin(noms)]
    evolution = pd.read_parquet(PROCESSED / "evolution_nationale.parquet")
    departements = pd.read_parquet(PROCESSED / "departements_2022.parquet")
    departements["departement"] = departements["code_departement"].map(noms)
    return contours, noms, votes, participation, evolution, departements


CONTOURS, NOMS, VOTES, PARTICIPATION, EVOLUTION, DEPARTEMENTS = charger_donnees()
ANNEES = sorted(VOTES["annee"].unique())

app = Dash(__name__, title="Présidentielles 2002-2027")

app.layout = html.Div(style={"fontFamily": "sans-serif", "maxWidth": "1200px", "margin": "auto"}, children=[
    html.H1("Présidentielles françaises : 2002-2022 et tendance 2027"),
    html.P("Résultats du 1er tour par département (data.gouv.fr). 2027 : tendance construite à partir des "
           "évolutions 2002-2022 et de la moyenne de 29 sondages. C'est une tendance, pas une prévision (2027* sur le curseur)."),
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
    ]),
])


def carte(df, colonne, titre, etiquette):
    fig = px.choropleth(df, geojson=CONTOURS, locations="code_departement", featureidkey="properties.code",
                        color=colonne, hover_name="departement", color_continuous_scale="Viridis",
                        labels={colonne: etiquette})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title=titre, margin=dict(l=0, r=0, t=40, b=0))
    return fig


@app.callback(Output("carte", "figure"), Input("famille", "value"), Input("annee", "value"))
def maj_carte(famille, annee):
    df = VOTES[(VOTES["famille"] == famille) & (VOTES["annee"] == annee)]
    titre = f"{FAMILLES[famille]} au 1er tour {annee}" + (" (tendance)" if annee == 2027 else "")
    fig = carte(df, "part_exprimes", titre, "Part des exprimés")
    fig.update_coloraxes(colorbar_tickformat=".0%")
    return fig


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


@app.callback(Output("carte-abstention", "figure"), Input("election-abstention", "value"))
def maj_abstention(election):
    df = PARTICIPATION[PARTICIPATION["id_election"] == election].copy()
    df["departement"] = df["code_departement"].map(NOMS)
    fig = carte(df, "taux_abstention", f"Abstention : {election}", "Abstention")
    fig.update_coloraxes(colorbar_tickformat=".0%")
    return fig


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


def _statsmodels_disponible():
    try:
        import statsmodels  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    # threaded=False : plotly n'aime pas créer plusieurs figures en même temps dans des threads différents.
    app.run(debug=False, threaded=False)
