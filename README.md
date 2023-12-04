# Liquidation Searcher

Orderly liquidations TPS scale with number of liquidators, so we implement an open source liquidator bot to make it easier to let other traders join the liquidation party.

This project contains two parts:

* A real-time async event-driven trading framework heavily inspired by [paradigmxyz/artemis](https://github.com/paradigmxyz/artemis).
* A liquidation searcher that uses the framework to search for liquidation opportunities.

You can read more details from the [docs](/docs)

## Source code structure

```sh
/docs                                - document
/src/liquidation_searcher            - source code root of the python code
/src/liquidation_searcher/main.py    - entry point of the liquidation searcher
/src/liquidation_searcher/collectors - collectors implementation
/src/liquidation_searcher/strategies - strategies implementation
/src/liquidation_searcher/executors  - executors implementation
/src/liquidation_searcher/engine     - engine implementation
/conf                                - configuration files of different environments
/deployment                          - reference systemd unit file
```

## Run on local machine

The project uses [poetry](https://python-poetry.org/) to manage dependencies and virtualenv.

```sh
# Required python >= 3.10, you may use asdf or pyenv to manage multiple python versions
pip install poetry
poetry install # install all dependencies in the virtualenv
poetry shell # spawn a shell within the virtual environment
# run it in company's vpn in qa environment or use the staging environment
# source secret envs from your .env file
python run src/liquidation_searcher/main.py -c conf/qa.yml
```

## Run with systemd

Reference the systemd unit file [liquidation_searcher_dev.service](/deployment/liquidation_searcher_dev.service)

## Run with docker or k8s

Reference the [Dockerfile](/Dockerfile), Note that you need to set the environment variables in the dockerfile or pass them in when running the container in k8s
