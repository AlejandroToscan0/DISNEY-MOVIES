from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
from collections import Counter

app = Flask(__name__)

# Cargar los datos
df = pd.read_csv("disney_plus_titles.csv")

# Preprocesamiento
df["date_added"] = pd.to_datetime(df['date_added'])
df['year_added'] = df['date_added'].dt.year
df['month_added'] = df['date_added'].dt.month
df['season_count'] = df['duration'].astype(str).str.extract(r'(\d+)')
df['season_count'] = pd.to_numeric(df['season_count'], errors='coerce')
df['duration'] = df['duration'].astype(str).str.extract(r'(\d+)')
df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

# Filtrar TV Shows y Movies
d1 = df[df["type"] == "TV Show"].copy()
d2 = df[df["type"] == "Movie"].copy()


# 📌 RUTA PRINCIPAL - MENÚ CON TABLA
@app.route('/')
def index():
    movies_table = d2[['title', 'type', 'rating', 'release_year']].head(10).to_html(classes="table table-striped", index=False)
    tvshows_table = d1[['title', 'type', 'rating', 'release_year']].head(10).to_html(classes="table table-striped", index=False)
    return render_template('index.html', movies_table=movies_table, tvshows_table=tvshows_table)


# 📊 GRAFICO 1: Distribución de contenido (Movies vs TV Shows)
@app.route('/content_distribution')
def content_distribution():
    grouped = df["type"].value_counts().reset_index()
    grouped.columns = ["type", "count"]

    trace = go.Pie(labels=grouped["type"], values=grouped["count"], pull=[0.05, 0])
    fig = go.Figure(data=[trace])
    graph = fig.to_html(full_html=False)
    
    return render_template('graph.html', title="Distribución de Contenido", graph=graph)


# 📊 GRAFICO 2: Contenido agregado por año
@app.route('/content_by_year')
def content_by_year():
    vc1 = d1["year_added"].value_counts().reset_index()
    vc1.columns = ["year_added", "count"]
    vc1 = vc1.sort_values("year_added")

    vc2 = d2["year_added"].value_counts().reset_index()
    vc2.columns = ["year_added", "count"]
    vc2 = vc2.sort_values("year_added")

    trace1 = go.Bar(x=vc1["year_added"], y=vc1["count"], name="TV Shows", marker=dict(color="#a678de"))
    trace2 = go.Bar(x=vc2["year_added"], y=vc2["count"], name="Movies", marker=dict(color="#6ad49b"))
    
    fig = go.Figure([trace1, trace2])
    graph = fig.to_html(full_html=False)

    return render_template('graph.html', title="Contenido Publicado por Año", graph=graph)


# 📊 GRAFICO 3: Duración de Películas
@app.route('/movie_duration')
def movie_duration():
    x1 = d2['duration'].dropna()

    if len(x1) > 0:
        fig = ff.create_distplot([x1], ['Duración'], bin_size=5, curve_type='normal', colors=["#6ad49b"])
        fig.update_layout(title_text='Distribución de la duración de las Películas')
        graph = fig.to_html(full_html=False)
    else:
        graph = "<h3>No hay datos válidos para graficar.</h3>"

    return render_template('graph.html', title="Distribución de Duración de Películas", graph=graph)


# 📊 GRAFICO 4: Rating en TV Shows y Movies
@app.route('/rating_distribution')
def rating_distribution():
    vc1 = d1["rating"].value_counts().reset_index()
    vc1.columns = ["rating", "count"]
    vc1 = vc1.sort_values("rating")

    vc2 = d2["rating"].value_counts().reset_index()
    vc2.columns = ["rating", "count"]
    vc2 = vc2.sort_values("rating")

    trace1 = go.Bar(x=vc1["rating"], y=vc1["count"], name="TV Shows", marker=dict(color="#a678de"))
    trace2 = go.Bar(x=vc2["rating"], y=vc2["count"], name="Movies", marker=dict(color="#6ad49b"))

    fig = go.Figure([trace1, trace2])
    graph = fig.to_html(full_html=False)

    return render_template('graph.html', title="Distribución del Rating en TV Shows y Movies", graph=graph)


if __name__ == '__main__':
    app.run(debug=True)
