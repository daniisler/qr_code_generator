# Free QR Code Generator

A small Flask website for creating QR codes from text or URLs. It is completely free to use: there are no accounts, paywalls, subscriptions, or expiring QR-code links.

This project was created to provide a straightforward alternative to "predatory" QR-code services that advertise a QR code, then ask for payment and can disable the QR code's destination after a subscription is cancelled. QR codes generated here contain the submitted data directly and do not depend on a hosted redirect service.

The code is mostly AI-generated, so I don't advice to get inspired a lot by it, so if you're a developer think twice before using it as a reference.

## Reach through the web

You can access the QR code generator online at: <https://qr.daniisler.ch> (mail me at [mail@daniisler.ch](mailto:mail@daniisler.ch) if the website is down for some reason).

## Run with Docker

```bash
docker compose up --build
```

Open <http://localhost:8500>.

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The generator supports error-correction settings, color and sizing options, optional logos, built-in sample pictures, previewing, and PNG downloads.
