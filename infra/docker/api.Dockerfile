FROM python:3.11-slim

WORKDIR /app/apps/api
COPY apps/api/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir \
    "fastapi>=0.115,<1.0" \
    "uvicorn[standard]>=0.34,<1.0" \
    "pydantic-settings>=2.8,<3.0" \
    "alembic>=1.15,<2.0" \
    "sqlalchemy>=2.0,<3.0" \
    "psycopg[binary]>=3.2,<4.0" \
    "argon2-cffi>=23.1,<26.0" \
    "google-auth>=2.40,<3.0" \
    "python-multipart>=0.0.20,<1.0" \
    "requests>=2.32,<3.0" \
    "ortools>=9.12,<10.0" \
    "openpyxl>=3.1,<4.0" \
    "pytest>=8.3,<10.0" \
    "httpx2>=0.1.0"
COPY apps/api ./
COPY tools /app/tools
ENV PYTHONPATH=/app/apps/api
EXPOSE 8000
