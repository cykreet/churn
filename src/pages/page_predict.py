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
					id="model-select",
					options=[
						{"label": "CORAL (Best Performing)", "value": "1"},
						{"label": "Random Forest", "value": "2"},
					],
					style={"max-width": "50%", "margin-bottom": "4em"},
				),
				html.Div(id="predict-input"),
			]
		)
	]
