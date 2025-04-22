import os
import dash_bootstrap_components as dbc

from dash import Dash, html

app = Dash(external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME])
app.layout = [
	html.A(children=[html.I(className="fa-solid fa-meteor", style={"font-size": "3em", "color": "red"})], href="/"),
]

if __name__ == "__main__":
	# https://render.com/docs/environment-variables#all-runtimes
	app.run(host="0.0.0.0", debug=os.environ.get("RENDER", "false") != "true")
