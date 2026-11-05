FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir pytest pytest-cov

ENV PYTHONPATH=/app

CMD ["python", "-m", "pytest", "tests", "-v"]
