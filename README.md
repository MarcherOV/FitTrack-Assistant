# 🏋️‍♂️ Gym Progress & Fitness Tracker Bot

A modern ecosystem designed to track fitness progress, workouts, and body measurements. The project consists of a high-performance **FastAPI** backend, a **Telegram Bot** client, and a **frontend** interface (Web & Telegram Mini App), all communicating via a secure REST API and fully containerized using Docker.

---

## 📑 Table of Contents

- [Demo](#-demo)
- [Tech Stack](#-tech-stack)
- [Project Overview](#-project-overview)
- [API Architecture & Principles](#-api-architecture--principles)
- [Project Structure](#-project-structure)
- [Docker Services](#-docker-services)
- [How to Run the Project Locally](#-how-to-run-the-project-locally)
- [Testing](#-testing)
- [Accessing the Services](#-accessing-the-services)
- [Stopping the Application](#-stopping-the-application)

---

## 📸 Demo

### 🤖 Telegram Bot

[https://github.com/user-attachments/assets/YOUR-BOT-VIDEO-ID](https://github.com/user-attachments/assets/c14c95a2-732a-4a00-b1ba-5d3a516d22e6)

<p align="center">
  <img width="1687" height="460" alt="Image" src="https://github.com/user-attachments/assets/c2a4004f-21b3-4e58-845d-d39ccbac408e" />
  <img width="1677" height="798" alt="Image" src="https://github.com/user-attachments/assets/ca8a4cca-e702-49a9-b5c1-425d41607457" />
  <img width="1678" height="882" alt="Image" src="https://github.com/user-attachments/assets/9e1ca7c8-1375-4674-b42f-ba693a21ff70" />
</p>

### 🌐 Web & Telegram Mini App

[https://github.com/user-attachments/assets/YOUR-FRONTEND-VIDEO-ID](https://github.com/user-attachments/assets/9dd9cad0-8115-4281-86a8-4788f3a89aea)

<p align="center">
  <img width="2547" height="997" alt="Image" src="https://github.com/user-attachments/assets/267b0981-f472-4d78-9ea8-a38df40f03e6" />
  <img width="456" height="706" alt="Image" src="https://github.com/user-attachments/assets/28b8b746-5f48-4ace-93dd-9bb54bf70eae" />
</p>

### 📘 API Docs (Swagger)

<p align="center">
  <img width="1442" height="1175" alt="Image" src="https://github.com/user-attachments/assets/4fe657c8-6064-4044-8f72-2fb3600582f8" />
  <img width="1441" height="1157" alt="Image" src="https://github.com/user-attachments/assets/1d8031b3-2a3b-4bad-a6a7-ff72a2a6ae97" />
  <img width="1452" height="872" alt="Image" src="https://github.com/user-attachments/assets/dd19a254-b6e3-4c20-8f32-7ff735b81712" />
</p>

---

## 🚀 Tech Stack

| Layer                | Technologies                                        |
| -------------------- | --------------------------------------------------- |
| **Backend**          | FastAPI, Pydantic v2, Uvicorn                       |
| **Database & Cache** | PostgreSQL 15, Redis 7, SQLAlchemy (Async), Alembic |
| **Testing**          | Pytest, pytest-asyncio, pytest-mock, HTTPX          |
| **Bot**              | Python 3.11, Aiogram v3, HTTPX                      |
| **Frontend**         | Vite, React, Tailwind CSS (Web & Telegram Mini App) |
| **Infrastructure**   | Docker, Docker Compose, Ngrok (public URL tunneling) |

---

## 📖 Project Overview

This project is built to manage the training process efficiently and consists of several core components:

1. **Core API (FastAPI)** — A high-performance, asynchronous RESTful API. It handles business logic, data persistence, and relations between users, workouts, exercises, and sets.
2. **Client (Aiogram Bot)** — A Telegram bot that serves as the primary user interface for quick tracking. It communicates with the FastAPI server using `httpx`, acting as a trusted client with Service-to-Service authentication.
3. **Frontend (Web & Telegram Mini App)** — A web application for a richer user interface. It is designed to run both inside Telegram and in a regular web browser. It is exposed via a public Ngrok tunnel, as Telegram requires secure HTTPS domains for authentication and Mini App integration.

---

## 📐 API Architecture & Principles

To keep the API clean, scalable, and easy to maintain, the project implements the following principles:

- **Shallow Nesting** — Sub-resources are kept flat. For example, creating a set doesn't require a deeply nested path like `/trainings/{id}/exercises/{id}/sets`, but is managed directly via `/training-exercises/{id}/sets` or `/sets/{id}`.
- **Strict REST Standards** — Proper usage of HTTP verbs (`GET` for fetching, `POST` for creation, `PATCH` for partial updates, `DELETE` for removal) and standard semantic status codes (`200 OK`, `201 Created`, `204 No Content`).
- **Asynchronous Operations** — Full async stack using SQLAlchemy `AsyncSession` and asynchronous API endpoints to handle high concurrent loads from Telegram users efficiently.
- **Separation of Concerns** — Distinct separation between Database Models (SQLAlchemy), Data Validation layers (Pydantic schemas), Routers, Data Access Layers (Repositories), and Tests.

---

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
│   │   ├── tests/            # Pytest test suite for API endpoints
│   │   └── main.py           # FastAPI entry point
│   ├── Dockerfile            # Backend Dockerfile
│   ├── pytest.ini            # Pytest configuration
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

---

## 🐳 Docker Services

The application is fully containerized using `docker-compose`. The following services are orchestrated:

| Service    | Description                                                    | Port   |
| ---------- | -------------------------------------------------------------- | ------ |
| `db`       | PostgreSQL 15 instance                                         | `5432` |
| `redis`    | Redis 7 instance for caching and queue management              | `6379` |
| `api`      | The FastAPI backend service                                    | `8000` |
| `bot`      | The Aiogram Telegram bot running as a background service       | —      |
| `frontend` | The web application                                            | `5173` |
| `ngrok`    | Exposes the frontend to the internet using a static domain tunnel | `4040` |

---

## 🚀 How to Run the Project Locally

Thanks to Docker, deploying the project takes just a few minutes. All necessary services start automatically.

### 📋 Prerequisites

Make sure you have the following installed on your machine:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 🛠 Step 1. Clone the repository

```bash
git clone https://github.com/MarcherOV/FitTrack-Assistant.git
cd FitTrack-Assistant
```

### ⚙️ Step 2. Configure Environment Variables

Create a `.env` file in the root directory of the project by copying the `.env.example` file:

```bash
cp .env.example .env
```

Open the `.env` file and fill it with your credentials:

```env
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

> [!NOTE]
> If you changed the database username or DB name in your `.env` file, replace `postgres` and `fittrack_db` in the command above accordingly.

---

## 🧪 Testing

The API is fully tested using **pytest**. The test suite includes unit and integration tests for:

- authentication
- user management
- workouts
- body measurements
- caching mechanisms

Database interactions and external dependencies are mocked using `pytest-mock` to ensure fast and isolated test execution.

To run the test suite, use the following command while the Docker containers are running:

```bash
docker-compose exec api pytest
```

> [!NOTE]
> Ensure your `pytest.ini` is properly configured for async test scopes.

---

## 🌐 Accessing the Services

Once successfully deployed, you can interact with the project via the following access points:

| Service                          | How to access                                                                                       |
| -------------------------------- | --------------------------------------------------------------------------------------------------- |
| **Telegram Bot**                 | Send `/start` to your bot in Telegram to launch the core interface                                  |
| **Frontend (Web & Mini App)**    | Your configured Ngrok URL (e.g., `https://property-nemeses-encroach.ngrok-free.dev/`). Works both inside Telegram and in a regular browser |
| **Backend API Docs (Swagger)**   | <http://localhost:8000/docs>                                                                        |
| **Ngrok Control Panel**          | <http://localhost:4040>                                                                             |

> [!WARNING]
> **Important note on localhost:** even when accessing the frontend in a regular desktop browser, **do not use `http://localhost:5173`**.
> Because the application integrates with Telegram, it requires a trusted domain for authentication. Opening `localhost` will result in a **"Bot domain invalid"** error. Always use the secure Ngrok HTTPS URL.

---

## 🛑 Stopping the Application

To stop and remove the containers, run:

```bash
docker-compose down
```
