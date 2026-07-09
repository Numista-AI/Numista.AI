# Use the official Python lightweight image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True

# Copy local code to the container image.
ENV APP_HOME=/app
WORKDIR $APP_HOME
COPY . ./
COPY NumisMate_Collection_Template.xlsx .

# Upgrade pip first to ensure the latest resolver handles complex dependency trees correctly.
RUN pip install --upgrade pip

# Install production dependencies.
RUN pip install --no-cache-dir --upgrade-strategy eager -r requirements.txt

# Run the web service on container startup using Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
