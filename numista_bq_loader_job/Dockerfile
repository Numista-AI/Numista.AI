FROM python:3.11-slim

WORKDIR /app

# Only install what the BQ loader needs
RUN pip install --no-cache-dir \
    google-cloud-bigquery==3.25.0 \
    google-cloud-storage==2.18.2

COPY numista_bq_loader.py .

CMD ["python", "numista_bq_loader.py"]
