# liquidation-searcher

Orderly liquidation searcher bot

## Run

```sh
# Required python >= 3.12, you may use asdf or pyenv to manage multiple python versions
pip install poetry
poetry install # install all dependencies in the virtualenv
poetry shell # spawn a shell within the virtual environment
# run it in company's vpn in qa environment or use the staging environment
# source secret envs from your .env file
python run src/liquidation_searcher/main.py -c conf/qa.yml
```
