import os

import dash_bootstrap_components as dbc
import joblib
import numpy as np
from dash import Dash, Input, Output, State, dcc, html
from keras import models

from pages.page_404 import get_404_page
from pages.page_home import create_choropleth_map, get_geo_churn_frame, get_home_page
from pages.page_predict import get_predict_page

app = Dash(external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME], suppress_callback_exceptions=True)
server = app.server
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
					"position": "fixed",
				},
			),
			html.Div(id="page-content", children=[], style={"width": "100%", "margin-left": "10%"}),
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


@app.callback(
	[
		Output("predict-output", "children"),
		Output("eval-toast", "is_open"),
		Output("eval-toast", "header"),
		Output("eval-toast", "children"),
		Output("eval-toast", "icon"),
	],
	Input("evaluate-button", "n_clicks"),
	[
		State("model-select", "value"),
		State("credit", "value"),
		State("gender", "value"),
		State("age", "value"),
		State("balance", "value"),
		State("has-card", "value"),
		State("tenure", "value"),
		State("active-member", "value"),
		State("salary", "value"),
		State("country", "value"),
	],
)
def evaluate_model(
	n_clicks, model_select, credit, gender, age, balance, has_card, tenure, active_member, salary, country
):
	if (
		not n_clicks
		or n_clicks == 0
		or not all([model_select, credit, gender, age, balance, tenure, active_member, salary, country])
	):
		return [None, None, None, None, None]

	if not model_select:
		return [
			None,
			True,
			"Model Selection",
			"Please select a model",
			"danger",
		]

	def to_binary(value):
		return 1 if value == "1" else 0

	input_features = np.array(
		[
			[
				int(credit),
				int(gender),
				int(age),
				float(balance),
				int(3),
				to_binary(has_card),
				int(tenure),
				to_binary(active_member),
				int(salary),
				to_binary(country == "FRA"),
				to_binary(country == "DEU"),
				to_binary(country == "ESP"),
			]
		]
	)

	model_map = {
		"coral": {
			"name": "Coral",
			"model_path": "coral.keras",
		},
		"random_forest": {
			"name": "Random Forest",
			"model_path": "random_forest.pkl",
		},
	}

	selected_model = model_map.get(model_select)
	file_dir = os.path.dirname(__file__)
	model_name = selected_model.get("name")
	model_path = os.path.join(file_dir, "models", selected_model.get("model_path"))
	model = load_model(model_path)
	# todo: coral and random forest outputs are different, handle here
	prediction = model.predict(input_features)[0]

	return [
		dbc.Card([dbc.CardHeader(html.P("Model Prediction")), dbc.CardBody([html.P(prediction)])]),
		True,
		model_name,
		f"Customer churn prediction successfully completed with {model_name} model.",
		"success",
	]


def load_model(model_path):
	if not os.path.exists(model_path):
		return None

	if model_path.endswith(".keras"):
		return models.load_model(model_path)

	if model_path.endswith(".pkl"):
		return joblib.load(model_path)


@app.callback(
	Output("predict-input", "children"),
	Input("model-select", "value"),
	prevent_initial_call=True,
)
def get_predict_input(value):
	return [
		dbc.Card(
			[
				dbc.CardHeader(
					[
						html.P(
							"Input new data to predict whether a customer will churn",
						)
					]
				),
				dbc.CardBody(
					[
						dbc.Form(
							children=[
								html.Div(
									[
										dbc.Label("Credit Score", html_for="credit"),
										dbc.Input(type="number", id="credit", placeholder="Enter credit score"),
										dbc.FormText(
											"Student's weekly study time in hours",
											color="secondary",
										),
									]
								),
								html.Div(
									[
										dbc.Label("Gender", html_for="gender"),
										dbc.Select(
											id="gender",
											options=[
												{"label": "Male", "value": 0},
												{
													"label": "Female",
													"value": 0,
												},
											],
										),
									]
								),
								html.Div(
									[
										dbc.Label("Age", html_for="age"),
										dbc.Input(type="number", id="age", placeholder="Enter customer age"),
									]
								),
								html.Div(
									[
										dbc.Label("Tenure", html_for="tenure"),
										dbc.Input(type="number", id="tenure", placeholder="Enter customer tenure"),
									]
								),
								html.Div(
									[
										dbc.Label("Balance", html_for="balance"),
										dbc.Input(type="number", id="balance", placeholder="Enter customer balance"),
									]
								),
								html.Div(
									[
										dbc.Label("Has Credit Card", html_for="has-card"),
										dbc.Select(
											id="has-card",
											options=[
												{"label": "Yes", "value": 1},
												{
													"label": "No",
													"value": 0,
												},
											],
										),
										dbc.FormText(
											"Does the customer have a credit card attached?",
											color="secondary",
										),
									]
								),
								html.Div(
									[
										dbc.Label("Active Member", html_for="active-member"),
										dbc.Select(
											id="active-member",
											options=[
												{"label": "Yes", "value": 1},
												{
													"label": "No",
													"value": 0,
												},
											],
										),
										dbc.FormText(
											"Does this customer have an active subscription?",
											color="secondary",
										),
									]
								),
								html.Div(
									[
										dbc.Label("Estimated Salary", html_for="salary"),
										dbc.Input(
											type="number", id="salary", placeholder="Enter customer estimated salary"
										),
									]
								),
								html.Div(
									[
										dbc.Label("Country", html_for="country"),
										dbc.Select(
											id="country",
											options=[
												{"label": "France", "value": "FRA"},
												{
													"label": "Germany",
													"value": "DEU",
												},
												{
													"label": "Spain",
													"value": "ESP",
												},
											],
										),
										dbc.FormText(
											"Does this customer have an active subscription?",
											color="secondary",
										),
									]
								),
								dbc.Button("Check Churn", id="evaluate-button", color="primary"),
							],
							className="form-spacer",
							style={"padding": "1em"},
						),
					]
				),
			],
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
