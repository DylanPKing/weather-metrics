FROM ghcr.io/astral-sh/uv:python3.14-trixie
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --no-cache --locked
COPY . .

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "8000"]