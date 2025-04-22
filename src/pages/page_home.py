from dash import html


def get_home_page():
	return [
		html.Div(
			children=[
				html.H1("Overview"),
				html.P("Observe patterns in your data at a glance with this overview page.", className="description"),
			]
		)
	]
