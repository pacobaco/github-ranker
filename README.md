# GitHub Ranker

A FastAPI service that ranks GitHub repositories using a transparent rubric, with authentication, monthly quotas, Stripe billing hooks, organization seats, and Docker/Postgres support.

## Ranking rubric

- **Uniqueness:** 30 points
- **Usage:** 20 points
- **Activity:** 15 points
- **Documentation:** 15 points
- **Purpose:** 10 points
- **Technical quality:** 10 points

Grades: A (85+), B (70+), C (55+), D (40+), F (<40).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set GITHUB_TOKEN and SECRET_KEY
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

SQLite is the development default. Docker Compose uses PostgreSQL.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## API

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /rank`
- `GET /rank/history`
- `POST /billing/checkout`
- `POST /billing/portal`
- `POST /billing/webhook`
- `POST /orgs`
- `GET /orgs/mine`
- `POST /orgs/{org_id}/invites`
- `POST /orgs/invites/{token}/accept`
- `DELETE /orgs/{org_id}/members/{user_id}`
- `POST /orgs/{org_id}/seats`

## Production notes

This is a runnable scaffold, not a production security/compliance package. Before deployment, add database migrations, tests, rate limiting, stronger password policy, secret management, Stripe subscription-state reconciliation, webhook idempotency, email delivery for invitations, audit logging, and production CORS settings.

## License

Add your preferred license before publishing.
