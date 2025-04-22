import os
import dash_bootstrap_components as dbc

from dash import Dash, Input, Output, html, dcc

from pages.page_404 import get_404_page
from pages.page_home import get_home_page
from pages.page_predict import get_predict_page

app = Dash(external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME])
app.layout = [
	html.Link(rel="stylesheet", href="styles.css"),
	dcc.Location(id="url", refresh=False),
	html.Div(
		children=[
			html.Div(
				children=[
					html.A(
						children=[
							html.I(
								className="fa-solid fa-meteor",
								style={"font-size": "3em", "color": "red", "margin-bottom": "1em"},
							)
						],
						href="/",
					),
					dbc.Nav(
						id="nav-items",
						pills=True,
						style={"marginTop": "auto", "gap": "1em", "display": "flex", "flex-direction": "column"},
					),
				],
				style={
					"display": "flex",
					"justify-content": "center",
					"flex-direction": "column",
					"max-width": "10%",
					"align-items": "center",
					"gap": "2em",
				},
			),
			html.Div(
				children=[html.Div(id="page-content", children=get_home_page())],
			),
		],
		style={"display": "flex", "flex-direciton": "row", "gap": "5em"},
		className="page-container",
	),
]


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_content(pathname):
	if pathname == "/predict":
		return get_predict_page()
	else:
		return get_home_page() if pathname == "/" else get_404_page()


@app.callback(Output("nav-items", "children"), Input("url", "pathname"))
def get_nav_items(pathname):
	if pathname == "/predict":
		return [
			dbc.NavItem(
				dbc.NavLink(
					children=html.I(className="fa-solid fa-home", style={"font-size": "1.3em", "color": "red"}),
					href="/",
				),
			),
			dbc.NavItem(
				dbc.NavLink(
					children=html.I(
						className="fa-solid fa-rectangle-list", style={"font-size": "1.3em", "color": "red"}
					),
					href="/predict",
					active=True,
				),
			),
		]
	else:
		return [
			dbc.NavItem(
				dbc.NavLink(
					children=html.I(className="fa-solid fa-home", style={"font-size": "1.3em", "color": "red"}),
					href="/",
					active=True,
				),
			),
			dbc.NavItem(
				dbc.NavLink(
					children=html.I(
						className="fa-solid fa-rectangle-list", style={"font-size": "1.3em", "color": "red"}
					),
					href="/predict",
				),
			),
		]


if __name__ == "__main__":
	# https://render.com/docs/environment-variables#all-runtimes
	app.run(host="0.0.0.0", debug=os.environ.get("RENDER", "false") != "true")
