# Web Bank

A full-stack banking platform that demonstrates how to build a modern retail bank with double-entry accounting, multi-factor authentication, and RESTful integrations — all wrapped in a container-first deployment story.

## Table of Contents
- [Overview](#overview)
- [Feature Highlights](#feature-highlights)
- [System Architecture](#system-architecture)
- [User Journeys](#user-journeys)
- [Security Posture](#security-posture)
- [API Surface](#api-surface)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Bootstrapping with Docker Compose](#bootstrapping-with-docker-compose)
- [Database Seeding](#database-seeding)
- [Quality & Developer Tooling](#quality--developer-tooling)
- [Deployment Notes](#deployment-notes)
- [Known Gaps & Next Steps](#known-gaps--next-steps)
- [Contributing](#contributing)

## Overview
Web Bank ("PayLater") is a Django 3.2 application that models end-to-end banking flows:
customers can review balances, move money, and request loans; staff members manage
KYC data and accounts; and the system can integrate with partner banks via token-secured
REST APIs. The stack is production-oriented out of the box with Dockerized services,
PostgreSQL, Gunicorn+Uvicorn, and an Nginx front door that optionally provisions TLS
via Certbot.

## Feature Highlights
- **Customer experience** – Responsive dashboards show balances, account history, and transaction drill-downs with consistent European formatting and localization (`bank/views.py:41`).
- **Operational tooling** – Staff-only workspace with HTMX live search, inline customer editing, and instant account provisioning without leaving the page (`bank/templates/bank/staff_dashboard.html:7`).
- **Double-entry ledger** – Every transfer and loan is journaled as paired debit/credit entries to keep balances accurate and auditable (`bank/models.py:178`).
- **Rank-aware lending** – Customer rank controls loan eligibility; approved loans provision a dedicated account and credit the customer automatically (`bank/models.py:92`).
- **External transfers** – Pending transfers route through a partner bank API, record metadata for reconciliation, and update statuses on completion (`bank/views.py:132`).
- **Two-factor authentication** – Login is guarded by `django-otp` TOTP MFA middleware and templates, providing step-up security for all users (`kea_bank/settings.py:61`).
- **Container-native ops** – Docker Compose orchestrates the Django app, PostgreSQL, and Nginx (with optional LetsEncrypt renewal) for dev, test, and prod tiers (`docker-compose.yml:5`).

## System Architecture
```
+---------------------------+        +-------------------+
|  Browser (staff/customer) |<----->|  Django (bank app) |
+---------------------------+        |  REST Framework    |
        ^    ^                        |  django-otp MFA    |
        |    |                        +---------+---------+
        |    |                                  |
        |    |                          Token-auth APIs
        |    v                                  |
+---------------------------+        +---------v---------+
|  HTMX partial updates     |        |  PostgreSQL DB    |
|  Classless CSS UI         |        |  Double-entry data|
+---------------------------+        +-------------------+
        ^
        |
        v
+---------------------------+
|  Nginx reverse proxy      |
|  Certbot (prod TLS)       |
+---------------------------+
```

Key components:
- **Django app (`bank/`)** – Forms, views, and templates that power customer and staff workflows.
- **REST layer (`api/`)** – DRF endpoints for interbank transactions and account lookups.
- **Management commands** – `provision` seeds account ranks; `demodata` spins up sample banks, customers, and journals for demos.
- **Environment-aware settings** – `RTE` flag toggles dev/test/prod behavior, including debug flags and secrets handling (`kea_bank/settings.py:24`).

## User Journeys
- **Customers** log in with MFA, land on a personal dashboard, review balances, initiate transfers, track pending external payments, and request loans when eligible.
- **Staff** members receive a dedicated portal to search customers, update contact/KYC data, inspect ledgers, and open new accounts in seconds using HTMX-powered forms.
- **Partner banks** integrate via REST endpoints to confirm external transfers and to query account holder metadata when required for payment initiation.

## Security Posture
- Enforced **token-based authentication** for API consumers with Django REST Framework (`kea_bank/settings.py:65`).
- **OTP middleware** ensures every login is verified with TOTP codes, backed by dedicated templates for challenge flows (`templates/registration/login.html:7`).
- Strict **double-entry accounting** guards against orphan ledger movements; every debit must pair with a credit under the same UID (`bank/models.py:178`).
- **CSRF** protection remains active for all HTML forms, and HTMX requests inject the CSRF token automatically (`templates/base.html:57`).
- Production configuration runs **Gunicorn behind Nginx**, with provisioning hooks for LetsEncrypt certificates and scheduled renewals (`nginx/Dockerfile:1`, `nginx/scheduler.txt:1`).

## API Surface
Base path: `/api/v1/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/transaction/create` | Accepts token-authenticated external transfers, journals both sides of the movement, and records reconciliation metadata (`bank/views.py:352`). |
| `GET`  | `/account/<account_number>` | Returns the account holder’s name for KYC or payment confirmation workflows (`bank/views.py:333`). |
| `POST` | `/api-token-auth/` | Issues DRF auth tokens for trusted partner banks (`kea_bank/urls.py:17`). |
| `POST` | `/rest-auth/login/` | Session-based authentication for REST clients needing cookie auth (courtesy of `django-rest-auth`). |
| `POST` | `/rest-auth/logout/` | Ends REST sessions cleanly. |

> **Note:** `transaction/confirm/<int>` and `transaction/cancel/<int>` routes are wired but currently share the same handler stub; they exist as placeholders for future settlement flows (`api/urls.py:11`).

## Getting Started
### Prerequisites
- Docker and Docker Compose v2+
- (Optional) Python 3.9+ and pip if you intend to run the app outside containers

### Environment Configuration
The project reads its configuration from environment variables. The most important ones are:

| Variable | Purpose | Example |
|----------|---------|---------|
| `RTE` | Runtime environment flag (`dev`, `test`, `prod`) | `dev` |
| `BANK_NAME` | Canonical name for the hosting bank; used across seed data and transfers | `PayLater` |
| `APP_IP_SCOPE` | Address Django binds to when running in dev containers | `0.0.0.0` |
| `POSTGRES_DB` | Postgres database name | `webbank` |
| `POSTGRES_USER` | Postgres user | `webbank` |
| `POSTGRES_PASSWORD` | Postgres password | `super-secret` |
| `DJANGO_SECRET_KEY` | (Prod/Test) Django secret key | _generate securely_ |

Create an environment file that matches your runtime. For local development you can start with `db_dev.env`:

```env
# db_dev.env
RTE=dev
BANK_NAME=PayLater
APP_IP_SCOPE=0.0.0.0
POSTGRES_DB=webbank
POSTGRES_USER=webbank
POSTGRES_PASSWORD=webbank
```

The Compose file expands `${RTE}` when selecting the env file and Nginx config, so export the same variable in your shell:

```bash
export RTE=dev
```

### Bootstrapping with Docker Compose
```bash
# Build and start the stack
export RTE=dev
export BANK_NAME=PayLater
export APP_IP_SCOPE=0.0.0.0
docker compose up --build

# In another terminal, run migrations and create a superuser if needed
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser
```

Once the services are healthy:
- Django app: `http://localhost:8000/`
- Reverse-proxied portal via Nginx: `http://localhost:8080/`

Log in with the superuser credentials or generate demo users (see below). MFA enrollment happens the first time a user logs in after enabling django-otp devices.

## Database Seeding
Use the built-in management commands to bootstrap ranks and demo data:

```bash
# Seed account ranks (Platinum, Gold, Silver, Bronze)
docker compose exec app python manage.py provision

# Populate demo customers, accounts, and ledger entries
docker compose exec app python manage.py demodata
```

The demo command provisions:
- Bank operational accounts (IPO, OPS, external in/out)
- Partner bank metadata (PayLater & PayNow)
- Sample customers (`dummy`, `john`) with funded checking accounts

## Quality & Developer Tooling
- `runsqa` helper watches the filesystem, runs `pylama`, and lints templates with `djlint` for rapid feedback (`./runsqa`).
- Linting configuration intentionally relaxes line-length rules (`pylama.ini`).
- Static assets live under `static/` with ready-made themes (`custom.css`, `holiday.css`) to tweak the classless base.

## Deployment Notes
- Set `RTE=prod` to switch Django into hardened mode (DEBUG off, secrets pulled from env, Gunicorn served via Nginx on port 8080).
- `nginx/prod/conf.d` expects LetsEncrypt certificates under `/etc/letsencrypt/live/ingimar.dk/`; adjust the server block to match your domain.
- Certbot is installed in the Nginx image and scheduled to renew daily at noon via cron (`nginx/scheduler.txt:1`).
- For staging environments, use `RTE=test` to reuse the alternative Nginx config while keeping Django debug disabled.

## Known Gaps & Next Steps
- **Serializer mismatch:** `ExternalMetadataSerializers` omits several model fields (`bank/models.py:198`), so external integrations may lack required data until the serializer is aligned.
- **Bank lookup stub:** `ApiHandleTransaction` retrieves the debit bank via a positional argument placeholder (`bank/views.py:357`), which should be replaced with authenticated context.
- **Metadata string repr:** `ExternalTransferMetaData.__str__` references `self.debit_bank`, which does not exist and will raise at runtime (`bank/models.py:215`).
- **UX polish:** The transfer form still carries a "Log In" button label — an easy win for clarity (`bank/templates/bank/make_transfer.html:8`).
- **Automated tests:** Both `bank/tests.py` and `api/tests.py` are placeholders; end-to-end and unit coverage would harden future changes.

