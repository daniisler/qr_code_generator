FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
	&& apt-get install --no-install-recommends -y libcairo2 \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY robots.txt sitemap.xml ./
COPY templates ./templates
COPY static ./static

EXPOSE 8500

CMD ["gunicorn", "--bind", "0.0.0.0:8500", "app:app"]
