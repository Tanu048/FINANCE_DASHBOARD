# Finance Dashboard API

A role-based backend system for managing financial records and generating dashboard insights.

---

## 🚀 Tech Stack

FastAPI · SQLAlchemy · SQLite · JWT · Argon2 · Pydantic · pytest

---

## ⚙️ Setup

```bash
git clone <repo-url>
cd finance_dashboard

python -m venv env
source env/bin/activate   # or env\Scripts\activate (Windows)

pip install -r requirements.txt
uvicorn main:app --reload
```

Open: http://127.0.0.1:8000
API Docs: `/docs`

---

## 🔑 Features

* JWT Authentication (login/register)
* Role-based access control:

  * **Viewer** → read-only
  * **Analyst** → read + analytics
  * **Admin** → full access
* Financial record CRUD
* Filters (type, category, date)
* Dashboard APIs:

  * Summary (income, expenses, balance)
  * Category breakdown
  * Monthly trends
  * Recent records
* Input validation + error handling
* Unit tests with isolated DB

---

## 📁 Structure

```
database/   → models, DB setup  
routers/    → API routes  
schema/     → request/response validation  
tests/      → unit tests  
main.py     → app entry  
```

---

## 🔌 API Overview

### Auth

* `POST /auth/register`
* `POST /auth/login`
* `GET /auth/me`

### Records

* `GET /records/` (filters supported)
* `POST /records/` (admin)
* `PUT /records/{id}` (admin)
* `DELETE /records/{id}` (admin)
* `GET /records/summary`
* `GET /records/by-category` (analyst+)
* `GET /records/trends` (analyst+)
* `GET /records/recent`

### Users (Admin)

* `GET /users/list`
* `PUT /users/{id}`
* `DELETE /users/{id}`

---

## 🔐 Roles

| Role    | Access           |
| ------- | ---------------- |
| Viewer  | Read only        |
| Analyst | Read + analytics |
| Admin   | Full access      |

---

## 🧠 Assumptions

* Data is shared across all users (not user-specific)
* SQLite used for simplicity
* Admin role can be assigned during registration (demo purpose)

---

## 🧪 Tests

```bash
pytest -v
```

---

## 💡 Notes

* Easily switch to PostgreSQL via `DATABASE_URL`
* Designed for clarity, correctness, and maintainability
* Focused on backend architecture and access control

---
