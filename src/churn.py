import os

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, dcc, html

from pages.page_404 import get_404_page
from pages.page_home import create_choropleth_map, get_geo_churn_frame, get_home_page
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
						style={"gap": "1em", "display": "flex", "flex-direction": "column"},
					),
				],
				style={
					"display": "flex",
					"flex-direction": "column",
					"max-width": "10%",
					"align-items": "center",
					"gap": "2em",
					"height": "50vh",
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


@app.callback(Output("choropleth-map", "figure"), [Input("metric-dropdown", "value")])
def update_map(selected_metric):
	return create_choropleth_map(selected_metric)


@app.callback(Output("country-details", "children"), [Input("choropleth-map", "clickData")])
def display_country_details(clickData):
	if not clickData:
		return html.P("Click on a country in the map to see detailed metrics.", className="text-muted")

	loc = clickData["points"][0]["location"]

	iso_to_country = {"FRA": "France", "DEU": "Germany", "ESP": "Spain"}
	country = next((c for iso, c in iso_to_country.items() if iso == loc), None)

	if not country:
		return html.P("Country data not available", className="text-danger")

	geo_churn_df = get_geo_churn_frame()
	country_data = geo_churn_df[geo_churn_df["Country"] == country].iloc[0]

	return [
		html.H4(country, className="card-title"),
		dbc.Table(
			[
				html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")])),
				html.Tbody(
					[
						html.Tr([html.Td("Total Customers"), html.Td(f"{country_data['Total_Customers']:,}")]),
						html.Tr([html.Td("Churned Customers"), html.Td(f"{country_data['Churned_Customers']:,}")]),
						html.Tr([html.Td("Churn Rate"), html.Td(f"{country_data['Churn_Rate']:.1%}")]),
						html.Tr([html.Td("Avg. Credit Score"), html.Td(f"{country_data['Avg_Credit_Score']:.1f}")]),
						html.Tr([html.Td("Avg. Age"), html.Td(f"{country_data['Avg_Age']:.1f}")]),
						html.Tr([html.Td("Avg. Balance"), html.Td(f"${country_data['Avg_Balance']:,.2f}")]),
						html.Tr([html.Td("Avg. Tenure"), html.Td(f"{country_data['Avg_Tenure']:.1f} years")]),
						html.Tr([html.Td("Active Member Rate"), html.Td(f"{country_data['Active_Member_Rate']:.1%}")]),
					]
				),
			],
			bordered=True,
			hover=True,
			striped=True,
			size="sm",
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
