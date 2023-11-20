FROM python:3.10-bookworm as builder

RUN pip install poetry

# https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
# https://python-poetry.org/docs/configuration/#using-environment-variables
ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install -n --without dev --no-root && rm -rf "$POETRY_CACHE_DIR"

FROM python:3.10-slim-bookworm as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src ./src
COPY ./conf/local.yml ./config.yml
EXPOSE 8088
CMD ["python", "src/liquidation_searcher/main.py", "-c", "config.yml"]
