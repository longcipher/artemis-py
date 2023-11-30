# liquidation-searcher

Orderly liquidation searcher bot

## Run

```sh
poetry install # install all dependencies in the virtualenv
poetry shell # spawn a shell within the virtual environment
# run it in company's vpn in qa environment or use the staging environment
python run src/liquidation_searcher/main.py -c conf/qa.yml
```
