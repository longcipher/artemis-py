# liquidation-searcher

liquidation arbitrage searcher

## Run

```sh
poetry install # install all dependencies in the virtualenv
poetry shell # spawn a shell within the virtual environment
python run src/liquidation_searcher/main.py -c conf/local.yml
```

## Tools

List all perp market symbols

```sh
python run src/liquidation_searcher/main.py -c conf/local.yml list_perp_symbols
```
