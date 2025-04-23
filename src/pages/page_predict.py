import dash_bootstrap_components as dbc

from dash import html


def get_predict_page():
	return [
		html.Div(
			children=[
				html.H1("Prediction"),
				html.P(
					"Input new data with a select machine learning model to predict whether a customer will churn.",
					className="description",
				),
				html.Span(children="SELECT MODEL", style={"font-weight": "bold", "font-size": "0.6em"}),
				dbc.Select(
					id="select",
					options=[
						{"label": "Model 1 (Best Performing)", "value": "1"},
						{"label": "Model 2", "value": "2"},
					],
					style={"max-width": "50%"},
				),
			]
		)
	]
