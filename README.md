# LocalServices: Subscription Marketplace for Local Service Providers

A full-stack Django marketplace where local service providers (plumbers, tutors, salons and more) subscribe to a plan, get listed and reviewed, and are automatically promoted to matching customers over **WhatsApp** and **Facebook**.

Built during my Full-Stack Development internship (May–Aug 2026). The project started in the company's Azure DevOps repository and was later mirrored here with their permission, so commit authorship in the history reflects the company's accounts.

## Features

- **Provider listings:** profiles, categories, city-based search, reviews and ratings with filtering and sorting, and referral/promo codes.
- **Subscriptions and payments:** Basic, Pro and Max plans, with **Razorpay** checkout and server-side payment signature verification.
- **Automatic outreach:** when a provider subscribes, a **Celery** worker matches customers by city and service interest and messages them through the **WhatsApp Business Cloud API** and Facebook. Every delivery attempt is logged.
- **Authentication:** signup and login through **Supabase Auth (JWT)**, linked to Django users, plus a REST API (`/api/v1/`).
- **Admin dashboard:** a super-admin dashboard alongside the Django admin (Jazzmin theme).
- **Pricing page:** a React + TypeScript + Vite pricing table, built with Tailwind.
- **SEO and performance:** sitemap, robots.txt, self-hosted fonts and icons, and build-time Tailwind for faster first paint.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python 3.11, Django 5.2, Django REST Framework |
| Database | PostgreSQL on Supabase (production), SQLite (local development) |
| Async and caching | Celery, Redis, django-redis |
| Auth | Supabase Auth, JWT (PyJWT) |
| Payments | Razorpay |
| Messaging | WhatsApp Business Cloud API, Facebook Graph API |
| Frontend | Django templates, React 19 + TypeScript (Vite), Tailwind CSS |
| Deployment | Docker, Gunicorn, WhiteNoise, Google Cloud Run |

## How outreach works

```
Provider pays (Razorpay) ──► Subscription activated
                                   │
                                   ▼
                     trigger_outreach (Celery task, retries ×3)
                                   │
           ┌───────────────────────┼────────────────────────┐
           ▼                       ▼                        ▼
  Match customers by       Cap by plan's reach      Send via WhatsApp and/or
  city + service interest  limit                    Facebook, log each attempt
```

The web request returns immediately. All matching and messaging runs in the background worker, so the site stays responsive under load.

## Project structure

```
localservices/      Django settings, URLs, Celery app
accounts/           Users, Supabase Auth signup/login API
services/           Service providers, reviews, referrals
customers/          Customer dataset used for outreach matching
subscriptions/      Plans, Razorpay checkout, payments
messaging/          Outreach models, WhatsApp/Facebook integrations, Celery tasks
projects/, activities/  Projects and activity log
admin_dashboard/    Super-admin dashboard
frontend_pricing/   React + Vite pricing table
templates/, static/ Server-rendered pages and assets
```

## Running locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in the values you need

python manage.py migrate
python manage.py seed_plans             # Basic / Pro / Max plans
python manage.py create_super_admin
python manage.py runserver
```

To process outreach jobs, run Redis and start a worker in a second terminal:

```bash
celery -A localservices worker -l info
```

If `DB_HOST` is not set, Django uses a local SQLite file. Set `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` and `DB_PORT` to use Supabase PostgreSQL.

### Environment variables

| Group | Variables |
|---|---|
| Django | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` |
| Database | `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` |
| Supabase | `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_JWT_SECRET` |
| Redis / Celery | `REDIS_URL` |
| Payments | `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_CURRENCY` |
| WhatsApp / Facebook | `WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, `FACEBOOK_PAGE_ACCESS_TOKEN` |
| Email | `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` |
| Optional | `GEMINI_API_KEY`, `SUPERCOMPRESS_API_KEY`, `GOOGLE_ANALYTICS_ID` |

Never commit a real `.env` file.

## Deployment

The `Dockerfile` builds the Tailwind CSS, collects static files, and serves the app with Gunicorn on port 8080, ready for Google Cloud Run:

```bash
docker build -t localservices .
docker run -p 8080:8080 --env-file .env localservices
```

## My contributions

- **Backend performance:** optimized Django ORM queries, added composite database indexes and Redis caching, cutting backend latency from **~200ms to under 15ms**.
- **Async outreach:** built the Celery + Redis worker that matches customers to providers and sends WhatsApp/Facebook messages, keeping the app responsive under load.
- **Auth and database:** integrated Supabase Auth (JWT) signup and login with Django users, set up Supabase PostgreSQL, and built the admin dashboard.
- **Deployment and payments:** containerized the app for Google Cloud Run, fixed production CSRF/SSL issues behind the load balancer, and built the Razorpay subscription checkout.
