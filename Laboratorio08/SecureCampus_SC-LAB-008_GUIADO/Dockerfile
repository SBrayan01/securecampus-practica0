FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system scapp && useradd --system --gid scapp --home-dir /app scapp \
    && mkdir -p /data && chown scapp:scapp /data
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt "gunicorn>=23,<24"
COPY src ./src
COPY docker_entry.py .
USER scapp
EXPOSE 8000
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "--worker-tmp-dir", "/tmp", "docker_entry:app"]
