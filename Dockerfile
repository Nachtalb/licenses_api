FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "licenses.main:app", "--host", "0.0.0.0", "--port", "8000"]
