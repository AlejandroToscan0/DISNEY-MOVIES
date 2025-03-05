from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
from collections import Counter

app = Flask(__name__)

# 📌 Cargar los datos
df = pd.read_csv("disney_plus_titles.csv")

# 📌 Preprocesamiento de datos
df["date_added"] = pd.to_datetime(df['date_added'], errors='coerce')
df['year_added'] = df['date_added'].dt.year
df['month_added'] = df['date_added'].dt.month

# Manejo de 'duration' y 'season_count'
df['season_count'] = df['duration'].astype(str).str.extract(r'(\d+)')
df['season_count'] = pd.to_numeric(df['season_count'], errors='coerce')

df['duration'] = df['duration'].astype(str).str.extract(r'(\d+)')
df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

# Filtrar TV Shows y Movies
d1 = df[df["type"] == "TV Show"].copy()
d2 = df[df["type"] == "Movie"].copy()

# 📌 Diccionario de códigos de países
country_codes = {
    'united states': 'USA', 'mexico': 'MEX', 'canada': 'CAN', 'brazil': 'BRA',
    'france': 'FRA', 'united kingdom': 'GBR', 'spain': 'ESP', 'italy': 'ITA',
    'germany': 'DEU', 'australia': 'AUS', 'japan': 'JPN', 'china': 'CHN',
    'india': 'IND', 'south korea': 'KOR', 'russia': 'RUS', 'argentina': 'ARG'
}

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

    fig = go.Figure(data=[go.Pie(labels=grouped["type"], values=grouped["count"], pull=[0.05, 0])])
    graph = fig.to_html(full_html=False)

    return render_template('graph.html', title="Distribución de Contenido", graph=graph)

# 📊 GRAFICO 2: Contenido agregado por año
@app.route('/content_by_year')
def content_by_year():
    def get_year_counts(data):
        vc = data["year_added"].value_counts().reset_index()
        vc.columns = ["year_added", "count"]
        return vc.sort_values("year_added")

    trace1 = go.Bar(x=get_year_counts(d1)["year_added"], y=get_year_counts(d1)["count"], name="TV Shows", marker=dict(color="#a678de"))
    trace2 = go.Bar(x=get_year_counts(d2)["year_added"], y=get_year_counts(d2)["count"], name="Movies", marker=dict(color="#6ad49b"))

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
    def get_rating_counts(data):
        vc = data["rating"].value_counts().reset_index()
        vc.columns = ["rating", "count"]
        return vc.sort_values("rating")

    trace1 = go.Bar(x=get_rating_counts(d1)["rating"], y=get_rating_counts(d1)["count"], name="TV Shows", marker=dict(color="#a678de"))
    trace2 = go.Bar(x=get_rating_counts(d2)["rating"], y=get_rating_counts(d2)["count"], name="Movies", marker=dict(color="#6ad49b"))

    fig = go.Figure([trace1, trace2])
    graph = fig.to_html(full_html=False)

    return render_template('graph.html', title="Distribución del Rating en TV Shows y Movies", graph=graph)

# 📊 GRAFICO 5: Contenido por País (Mapa Mundial y Barras)
@app.route('/content_by_country')
def content_by_country():
    country_count = Counter(", ".join(df['country'].dropna()).split(", "))
    country_with_code = {country_codes.get(c.lower(), None): v for c, v in country_count.items() if country_codes.get(c.lower(), None)}

    # Mapa Mundial
    fig_map = go.Figure(data=[
        go.Choropleth(
            locations=list(country_with_code.keys()),
            z=list(country_with_code.values()),
            colorscale="Blues",
            marker_line_color='gray',
            colorbar_title="Cantidad de Contenido"
        )
    ])
    fig_map.update_layout(title="Distribución de Contenido por País", geo=dict(showframe=False, showcoastlines=False, projection=dict(type="natural earth")))
    graph_map = fig_map.to_html(full_html=False)

    # Gráfico de Barras - Países con más contenido
    top_countries = Counter(country_count).most_common(15)
    labels, values = zip(*top_countries[::-1])

    fig_bars = go.Figure(data=[go.Bar(y=labels, x=values, orientation="h", marker=dict(color="#a678de"))])
    fig_bars.update_layout(title="Top 15 Países con Más Contenido", height=600, margin=dict(l=100, r=10, t=50, b=50))
    graph_bars = fig_bars.to_html(full_html=False)

    return render_template('graph_country.html', title="Contenido por País", graph_map=graph_map, graph_bars=graph_bars)

if __name__ == '__main__':
    app.run(debug=True)
