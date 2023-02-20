FROM python:3.10
WORKDIR /opt/app
COPY bot/ bot/
COPY credentials.json pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --without dev
ENV PORT=9444
ENTRYPOINT gunicorn --bind :$PORT --log-level DEBUG "bot.app:create_app()" --timeout 0