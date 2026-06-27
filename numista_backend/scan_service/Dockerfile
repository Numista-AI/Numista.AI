# Build: 2026-06-13 14:11:01
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python source modules
COPY main.py .
COPY estate_state_rules.py .
COPY estate_report_generator.py .
COPY estate_pdf_builder.py .
COPY estate_qr_generator.py .

ENV PORT=8080
EXPOSE 8080

# Timeout raised to 300s — estate PDF generation for 2000+ coin collections
# can take 60-120 seconds (Firestore fetch + Gemini + PDF build).
# 2 workers is correct for Cloud Run (CPU-bound PDF generation).
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "300", "main:app"]
