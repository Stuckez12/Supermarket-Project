FROM python:3.13-slim AS base

WORKDIR /app

# Prevents writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

# Copy the project files and install the dependencies
COPY requirements.txt  /app/
RUN pip install --no-cache-dir -r requirements.txt

# After base we don't need requirements.txt anymore

FROM python:3.13-slim AS prod

# Create a non-root user
RUN useradd -r appuser && mkdir /app && chown -R appuser /app

COPY --from=base /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/

WORKDIR /app
COPY --chown=appuser:appuser . .
RUN rm -rf .git .github .venv

# Prevents writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 50050

ENV PYTHONPATH=/app/src/backend_services/common/proto
CMD ["python", "-m", "src.backend_services.user_api_gateway.v1.server"]
