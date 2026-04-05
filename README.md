# Finance Dashboard API 🚀

A professional, role-based backend system designed to manage financial records and generate real-time dashboard insights. Built with **FastAPI**, this project focuses on clean architecture, secure authentication, and granular Access Control (RBAC).

**Live Demo:** [finance-dashboard-3aws.onrender.com](https://finance-dashboard-3aws.onrender.com/)  
**API Documentation:** [/docs](https://finance-dashboard-3aws.onrender.com/docs) (Swagger UI)

---

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python 3.11)
* **Database:** SQLite with SQLAlchemy ORM (Architecture ready for PostgreSQL)
* **Security:** JWT Authentication & Argon2 Password Hashing
* **Validation:** Pydantic v2
* **Testing:** Pytest with isolated database sessions

---

## 🔐 Role-Based Access Control (RBAC)

The system enforces strict access boundaries using FastAPI dependency injection to ensure data integrity and security:

| Role | Access Level | Permissions |
| :--- | :--- | :--- |
| **Viewer** | Read-Only | Can view records, summaries, and recent activity. |
| **Analyst** | Insights | All Viewer permissions + Monthly Trends and Category breakdowns. |
| **Admin** | Full Access | Complete CRUD on records and full User Management (Roles/Status). |

---

## 🔌 API Overview

### Authentication
* `POST /auth/register` - Create a new account.
* `POST /auth/login` - Exchange credentials for a JWT Bearer token.
* `GET /auth/me` - Retrieve the current authenticated user's profile.

### Financial Records
* `GET /records/` - List records with support for Type, Category, and Date range filtering.
* `POST /records/` - Create a new financial entry (**Admin only**).
* `GET /records/summary` - Total Income, Expenses, and Net Balance.
* `GET /records/trends` - Time-series data bucketed by month (**Analyst+**).
* `GET /records/by-category` - Aggregated spending/income by category (**Analyst+**).

### User Management
* `GET /users/list` - View all registered users (**Admin only**).
* `PUT /users/{id}` - Update a user's role or toggle active/inactive status.
* `DELETE /users/{id}` - Remove a user account and associated records.

---

## 🧠 Technical Assumptions & Decisions

* **Organizational Data Scope:** Financial records are treated as shared organizational data visible to authorized roles, simulating a corporate finance environment.
* **Demo Registration Flow:** For assessment purposes, `Admin` or `Analyst` roles can be claimed during registration by providing a pre-shared `ADMIN_KEY` (configured via Environment Variables).
* **Input Integrity:** Custom Pydantic validators ensure that `amount` is always positive and categories are sanitized/standardized.
* **Persistence:** SQLite is utilized for a zero-configuration setup, while the codebase remains database-agnostic via SQLAlchemy.

---

## ⚙️ Setup & Installation

1.  **Clone & Navigate:**
    ```bash
    git clone <repo-url>
    cd finance_dashboard
    ```

2.  **Environment Setup:**
    ```bash
    python -m venv env
    source env/bin/activate  # Windows: env\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Run Application:**
    ```bash
    uvicorn main:app --reload
    ```
    Access the local server at `http://127.0.0.1:8000`.

---

## 🧪 Automated Testing

The project includes a comprehensive test suite to verify business logic, security guards, and API responses.

```bash
pytest -v

```
Note: Tests use an isolated in-memory SQLite instance to ensure the production database remains clean.

## 📁 Project Structure

database/   → models, DB setup  
routers/    → API routes (auth, users, records)  
schema/     → request/response validation  
tests/      → unit tests  
main.py     → app entry  