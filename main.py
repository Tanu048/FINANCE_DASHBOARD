"""
Finance Dashboard — entry point.

Registers routers, mounts static files, serves Jinja2 templates,
and creates database tables on startup.
"""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database.db import create_tables
from routers import auth, records, users

# Logging

# Create logs directory before logging is configured — required on fresh deploys
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# App

app = FastAPI(
    title="Finance Dashboard API",
    description="Role-based finance record management system.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router,    prefix="/auth",    tags=["Auth"])
app.include_router(records.router, prefix="/records", tags=["Records"])
app.include_router(users.router,   prefix="/users",   tags=["Users"])

templates = Jinja2Templates(directory="templates")


# Page routes 

@app.get("/", include_in_schema=False)
def home(request: Request):
    """Render the landing page."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/login", include_in_schema=False)
def login_page(request: Request):
    """Render the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", include_in_schema=False)
def register_page(request: Request):
    """Render the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", include_in_schema=False)
def dashboard_page(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})
