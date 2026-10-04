FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates ./templates
COPY static ./static

EXPOSE 8500

CMD ["gunicorn", "--bind", "0.0.0.0:8500", "app:app"]
