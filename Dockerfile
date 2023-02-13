FROM python:3.10
WORKDIR /opt/app
COPY bot/ bot/
COPY poetry.lock pyproject.toml credentials.json ./
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install
ENTRYPOINT ["poetry", "run", "start"]