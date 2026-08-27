# 🏋️‍♂️ Gym Progress & Fitness Tracker Bot

A modern, production-ready ecosystem designed to track fitness progress, workouts, and body measurements. The project consists of a high-performance FastAPI backend, a Telegram Bot client, and a frontend interface, all communicating via a secure REST API and fully containerized using Docker.

## 🚀 Tech Stack

* **Backend:** FastAPI, Pydantic v2, Uvicorn
* **Database & Cache:** PostgreSQL 15, Redis 7, SQLAlchemy (Async), Alembic
* **Bot:** Python 3.11, Aiogram v3, HTTPX
* **Frontend:** Vite, React, Tailwind CSS (Port 5173)
* **Infrastructure:** Docker, Docker Compose, Ngrok (for public URL tunneling)

## 📖 Project Overview

This project is built to manage the training process efficiently and consists of several core components:
1. **Core API (FastAPI):** A high-performance, asynchronous RESTful API. It handles business logic, data persistence, and relations between users, workouts, exercises, and sets.
2. **Client (Aiogram Bot):** A Telegram bot that serves as the primary user interface for quick tracking. It communicates with the FastAPI server using `httpx`, acting as a trusted client with Service-to-Service authentication.
3. **Frontend:** A web application for a richer user interface, accessible via a public Ngrok tunnel.

## 📐 API Architecture & Principles

To keep the API clean, scalable, and easy to maintain, the project implements the following principles:

* **Shallow Nesting:** Sub-resources are kept flat. For example, creating a set doesn't require a deeply nested path like `/trainings/{id}/exercises/{id}/sets`, but is managed directly via `/training-exercises/{id}/sets` or `/sets/{id}`.
* **Strict REST Standards:** Proper usage of HTTP verbs (`GET` for fetching, `POST` for creation, `PATCH` for partial updates, `DELETE` for removal) and standard semantic status codes (`200 OK`, `201 Created`, `204 No Content`).
* **Asynchronous Operations:** Full async stack using `SQLAlchemy AsyncSession` and asynchronous API endpoints to handle high concurrent loads from Telegram users efficiently.
* **Separation of Concerns:** Distinct separation between Database Models (SQLAlchemy), Data Validation layers (Pydantic schemas), Routers, and Data Access Layers (Repositories).

## 🗂 Project Structure

```text
├── backend/                  # Core API (FastAPI)
│   ├── src/
│   │   ├── alembic/          # Database migrations
│   │   ├── api/
│   │   │   └── routers/      # API endpoints (auth, body, exercises, training, users)
│   │   ├── core/             # Configuration & security (config.py, security.py)
│   │   ├── db/               # DB connection & setup (database.py)
│   │   ├── models/           # SQLAlchemy models
│   │   ├── pagination/       # Pagination logic
│   │   ├── repositories/     # Repository pattern for DB access layer
│   │   ├── schemas/          # Pydantic models for validation
│   │   ├── scripts/          # Helper scripts
│   │   └── main.py           # FastAPI entry point
│   ├── Dockerfile            # Backend Dockerfile
│   └── requirements.txt
├── bot/                      # Telegram Bot Client (Aiogram)
│   ├── exceptions/           # Custom error handling
│   ├── handlers/             # Message handlers (start, body, training, etc.)
│   ├── keyboards/            # Telegram Reply/Inline keyboards
│   ├── middlewares/          # Request interceptors
│   ├── services/             # Business logic (api_client.py, set_collector.py)
│   ├── Dockerfile
│   ├── main.py               # Bot entry point
│   └── requirements.txt
├── frontend/                 # Client Web Interface (React/Vite)
│   ├── public/               # Static assets
│   ├── src/                  # Application source code
│   │   ├── api/              # API communication layer
│   │   ├── components/       # Reusable React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── utils/            # Utility functions
│   │   ├── App.jsx           # Main application component
│   │   ├── index.css         # Global styles
│   │   └── main.jsx          # React entry point
│   ├── Dockerfile            # Frontend Dockerfile
│   ├── index.html            # Main HTML template
│   ├── package.json          # Node.js dependencies
│   ├── postcss.config.js     # PostCSS configuration
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── vite.config.js        # Vite bundler configuration
├── .env.example              # Template for environment variables
├── docker-compose.yml        # Docker orchestration
├── alembic.ini               # Alembic configuration
└── seed.sql                  # Initial database seed script
```

## 🐳 Docker Services

The application is fully containerized using `docker-compose`. The following services are orchestrated:

* **`db`**: PostgreSQL 15 instance.
* **`redis`**: Redis 7 instance for caching and queue management.
* **`api`**: The FastAPI backend service running on port `8000`.
* **`bot`**: The Aiogram Telegram bot running as a background service.
* **`frontend`**: The web application running on port `5173`.
* **`ngrok`**: Exposes the frontend service to the internet using a static domain tunnel.

## 🚀 How to Run the Project Locally

Thanks to Docker, deploying the project takes just a few minutes. All necessary services start automatically.

### 📋 Prerequisites
Make sure you have the following installed on your machine:
* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)

### 🛠 Step 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/fittrack-assistant.git
cd fittrack-assistant
```

### ⚙️ Step 2. Configure Environment Variables
Create a `.env` file in the root directory of the project by copying the `.env.example` file:

```bash
cp .env.example .env
```

Open the `.env` file and fill it with your credentials:

```ini
# --- Database Settings ---
DB_NAME=fittrack_db
DB_USER=postgres
DB_PASSWORD=your_db_password_here
DB_HOST=db
DB_PORT=5432

# --- Telegram Bot Settings ---
TELEGRAM_TOKEN=123456789:YOUR_TELEGRAM_BOT_TOKEN_HERE

# --- Security & Authentication (FastAPI) ---
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# --- Ngrok Settings ---
NGROK_AUTHTOKEN=your_ngrok_auth_token_here
```

### 🐳 Step 3. Build and Run Containers
Execute the following command to build the images and run all services in detached mode:

```bash
docker-compose up -d --build
```

### 🗄 Step 4. Database Initialization (First Run)
After the containers have successfully started, you need to create the database tables and populate them with initial data (exercises, categories, etc.):

1. **Apply Alembic migrations** (creates tables):
   ```bash
   docker-compose exec api alembic upgrade head
   ```
2. **Load initial data** from the SQL seed script:
   ```bash
   docker-compose exec -T db psql -U postgres -d fittrack_db -f - < seed.sql
   ```
   *(Note: If you changed the database username or DB name in your `.env` file, replace `postgres` and `fittrack_db` in the command above accordingly).*

### 🌐 Accessing the Services
Once successfully deployed, you can interact with the project via the following access points:
* **Telegram Bot:** Just send `/start` to your bot in Telegram.
* **Frontend (React/Vite):** [http://localhost:5173](http://localhost:5173)
* **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Ngrok Control Panel:** [http://localhost:4040](http://localhost:4040)

## 🛑 Stopping the Application
To stop and remove the containers, run:
```bash
docker-compose down
```