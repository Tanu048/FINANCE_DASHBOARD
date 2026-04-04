# Finance Dashboard API

A role-based finance record management system built with FastAPI and SQLite.

Live Demo: _deploy URL here_
API Docs: `/docs`

---

## Tech Stack

FastAPI · SQLite · SQLAlchemy · PyJWT · Argon2 · Pydantic · pytest

---

## Setup

```bash
git clone <repo-url>
cd finance_dashboard

python -m venv env
env\Scripts\activate        # Windows
source env/bin/activate     # Mac / Linux

pip install -r requirements.txt

uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000`

No `.env` file is required for local development. The app uses SQLite and creates `finance.db` automatically on first run.

---

## Project Structure

```
finance_dashboard/
├── main.py                 # App entry point, page routes, logging setup
├── database/
│   ├── db.py               # SQLite engine, session factory, get_db dependency
│   └── models.py           # SQLAlchemy User and Record models
├── routers/
│   ├── auth.py             # /auth — register, login, me, role guards
│   ├── records.py          # /records — CRUD, summary, analytics
│   └── users.py            # /users — admin user management
├── schema/
│   ├── auths.py            # Token response schema
│   ├── users.py            # User create/update/response schemas
│   └── records.py          # Record create/update/response schemas
├── static/
│   ├── style.css           # All styles
│   └── scripts.js          # All frontend JS
├── templates/
│   ├── base.html           # Base template (all pages inherit from this)
│   ├── home.html           # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Register page
│   └── dashboard.html      # Main dashboard
├── tests/
│   ├── conftest.py         # Shared fixtures (test DB, client, tokens)
│   ├── test_auth.py        # Tests for auth functions and routes
│   ├── test_records.py     # Tests for records routes
│   └── test_users.py       # Tests for users routes
├── logs/
│   └── app.log             # Written at runtime (git-ignored)
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Environment Variables

| Variable         | Description                              | Default                    |
|------------------|------------------------------------------|----------------------------|
| `DATABASE_URL`   | SQLAlchemy connection string             | `sqlite:///./finance.db`   |
| `SECRET_KEY`     | JWT signing secret                       | `dev-secret-change-in-prod`|
| `ALGORITHM`      | JWT algorithm                            | `HS256`                    |
| `EXPIRE_MINUTES` | Token expiry in minutes                  | `60`                       |

---

## API Endpoints

### Auth

| Method | Path              | Auth | Description              |
|--------|-------------------|------|--------------------------|
| POST   | `/auth/register`  | No   | Register a new user      |
| POST   | `/auth/login`     | No   | Login, returns JWT token |
| GET    | `/auth/me`        | Yes  | Get current user profile |

### Records

| Method | Path                    | Auth          | Description                          |
|--------|-------------------------|---------------|--------------------------------------|
| GET    | `/records/`             | All roles     | List records (with filters)          |
| GET    | `/records/summary`      | All roles     | Total income, expenses, net balance  |
| GET    | `/records/recent`       | All roles     | Latest N records                     |
| GET    | `/records/by-category`  | Analyst+      | Totals grouped by category           |
| GET    | `/records/trends`       | Analyst+      | Monthly income vs expense buckets    |
| GET    | `/records/{id}`         | All roles     | Get single record                    |
| POST   | `/records/`             | Admin only    | Create a record                      |
| PUT    | `/records/{id}`         | Admin only    | Update a record                      |
| DELETE | `/records/{id}`         | Admin only    | Delete a record                      |

Query filters for `GET /records/`: `type`, `category` (partial), `from_date`, `to_date`

### Users

| Method | Path            | Auth       | Description                     |
|--------|-----------------|------------|---------------------------------|
| GET    | `/users/list`   | Admin only | List all users                  |
| PUT    | `/users/{id}`   | Admin only | Update role or active status    |
| DELETE | `/users/{id}`   | Admin only | Delete user (cascades records)  |

---

## Roles

| Role     | Records (view) | Records (write) | Analytics | User Management |
|----------|:--------------:|:---------------:|:---------:|:---------------:|
| viewer   | ✓              | ✗               | ✗         | ✗               |
| analyst  | ✓              | ✗               | ✓         | ✗               |
| admin    | ✓              | ✓               | ✓         | ✓               |

Role guards are implemented as FastAPI dependencies (`require_analyst`, `require_admin`) in `routers/auth.py` and injected directly into each route.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use an isolated `test.db` SQLite file. Each test resets the database for full isolation.

---

## Deploying to Render

**Option A — SQLite (simplest):**
Works as-is. Note: Render's free tier has an ephemeral filesystem, so `finance.db` resets on each restart. Fine for a demo.

**Option B — Free PostgreSQL on Render:**
Render provides one free PostgreSQL database (valid 90 days).

1. Create a PostgreSQL instance in the Render dashboard.
2. Copy the connection string.
3. Set `DATABASE_URL` in your Render web service environment variables:
   ```
   DATABASE_URL=postgresql://user:password@host/dbname
   ```
4. In `database/db.py`, change the `create_engine` call to remove `connect_args` (SQLite-only):
   ```python
   engine = create_engine(DATABASE_URL)
   ```

That is the only code change needed.

---

## Assumptions

1. **Records are org-wide** — all authenticated users see all financial records. This matches a typical finance dashboard where data is company-wide rather than per-user.
2. **Three roles** (viewer, analyst, admin) are used instead of two. This cleanly separates read-only access from analytics access.
3. **No admin key gate** — admin role is self-assigned at registration. In production you would restrict this (e.g. require an invite token).
4. **SQLite by default** — zero setup, appropriate for an assessment. One-line swap to PostgreSQL for a live deployment.
5. **No soft delete** — records and users are hard-deleted to keep the data model simple.
6. **No seeded data** — the app starts with an empty database. Register an account to get started.

---

## What to tell the interviewer

> "I built a finance record management API with FastAPI and SQLite. The core focus is role-based access — three roles: viewer, analyst, and admin — each enforced at the backend level, not just the UI. Viewers can read records and the summary. Analysts additionally get access to category breakdowns and monthly trends. Admins have full CRUD on records and can manage users. I chose FastAPI because it enforces request and response contracts through Pydantic, gives you automatic API docs, and makes dependency injection clean — each route just declares which role guard it needs. For password hashing I used Argon2, which won the Password Hashing Competition and is the current best practice over bcrypt. For the database I used SQLite so there is zero setup, and SQLAlchemy makes it a one-line swap to PostgreSQL. The project has unit tests for every route and function, structured logs, and all templates inherit from a single base.html."
