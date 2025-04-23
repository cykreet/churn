<img src="./src/assets/churn.png" width="200" />

# Development

This project uses [Poetry](https://python-poetry.org/) for dependency management and [Dash](https://dash.plotly.com/) for the web application framework.

1. First, install poetry:

Linux, macOS, Windows (WSL)
```
curl -sSL https://install.python-poetry.org | python3 -
```

Windows (Powershell)
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
2. `poetry install` to install defined dependencies
3. `python src/churn.py` or `poetry run python src/churn.py` to run dash app on `0.0.0.0:8050`