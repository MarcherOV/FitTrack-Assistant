🏋️‍♂️ Gym Progress & Fitness Tracker BotA modern, production-ready ecosystem designed to track fitness progress, workouts, and body measurements. The project consists of a high-performance FastAPI backend, a Telegram Bot client, and a frontend interface (Web & Telegram Mini App), all communicating via a secure REST API and fully containerized using Docker.🚀 Tech StackBackend: FastAPI, Pydantic v2, UvicornDatabase & Cache: PostgreSQL 15, Redis 7, SQLAlchemy (Async), AlembicTesting: Pytest, pytest-asyncio, pytest-mock, httpxBot: Python 3.11, Aiogram v3, HTTPXFrontend: Vite, React, Tailwind CSS (Web & Telegram Mini App)Infrastructure: Docker, Docker Compose, Ngrok (for public URL tunneling)📖 Project OverviewThis project is built to manage the training process efficiently and consists of several core components:Core API (FastAPI): A high-performance, asynchronous RESTful API. It handles business logic, data persistence, and relations between users, workouts, exercises, and sets.Client (Aiogram Bot): A Telegram bot that serves as the primary user interface for quick tracking. It communicates with the FastAPI server using httpx, acting as a trusted client with Service-to-Service authentication.Frontend (Web & Telegram Mini App): A web application for a richer user interface. It is designed to run both inside Telegram and in a regular web browser. It is exposed via a public Ngrok tunnel, as Telegram requires secure HTTPS domains for authentication and Mini App integration.📐 API Architecture & PrinciplesTo keep the API clean, scalable, and easy to maintain, the project implements the following principles:Shallow Nesting: Sub-resources are kept flat. For example, creating a set doesn't require a deeply nested path like /trainings/{id}/exercises/{id}/sets, but is managed directly via /training-exercises/{id}/sets or /sets/{id}.Strict REST Standards: Proper usage of HTTP verbs (GET for fetching, POST for creation, PATCH for partial updates, DELETE for removal) and standard semantic status codes (200 OK, 201 Created, 204 No Content).Asynchronous Operations: Full async stack using SQLAlchemy AsyncSession and asynchronous API endpoints to handle high concurrent loads from Telegram users efficiently.Separation of Concerns: Distinct separation between Database Models (SQLAlchemy), Data Validation layers (Pydantic schemas), Routers, Data Access Layers (Repositories), and Tests.🗂 Project Structure├── backend/                  # Core API (FastAPI)
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
🐳 Docker ServicesThe application is fully containerized using docker-compose. The following services are orchestrated:db: PostgreSQL 15 instance.redis: Redis 7 instance for caching and queue management.api: The FastAPI backend service running on port 8000.bot: The Aiogram Telegram bot running as a background service.frontend: The web application running on port 5173.ngrok: Exposes the frontend service to the internet using a static domain tunnel.🚀 How to Run the Project LocallyThanks to Docker, deploying the project takes just a few minutes. All necessary services start automatically.📋 PrerequisitesMake sure you have the following installed on your machine:DockerDocker Compose🛠 Step 1. Clone the repositorygit clone https://github.com/YOUR_USERNAME/fittrack-assistant.git
cd fittrack-assistant
⚙️ Step 2. Configure Environment VariablesCreate a .env file in the root directory of the project by copying the .env.example file:cp .env.example .env
Open the .env file and fill it with your credentials:# --- Database Settings ---
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
🐳 Step 3. Build and Run ContainersExecute the following command to build the images and run all services in detached mode:docker-compose up -d --build
🗄 Step 4. Database Initialization (First Run)After the containers have successfully started, you need to create the database tables and populate them with initial data (exercises, categories, etc.):Apply Alembic migrations (creates tables):docker-compose exec api alembic upgrade head
Load initial data from the SQL seed script:docker-compose exec -T db psql -U postgres -d fittrack_db -f - < seed.sql
(Note: If you changed the database username or DB name in your .env file, replace postgres and fittrack_db in the command above accordingly).🧪 TestingThe API is fully tested using pytest. The test suite includes unit and integration tests for authentication, user management, workouts, body measurements, and caching mechanisms. Database interactions and external dependencies are mocked using pytest-mock to ensure fast and isolated test execution.To run the test suite, use the following command while the Docker containers are running:docker-compose exec api pytest
(Note: Ensure your pytest.ini is properly configured for async test scopes).🌐 Accessing the ServicesOnce successfully deployed, you can interact with the project via the following access points:Telegram Bot: Send /start to your bot in Telegram to launch the core interface.Frontend (Web & Telegram Mini App): Access via your configured Ngrok URL (e.g., https://property-nemeses-encroach.ngrok-free.dev/). This link works both inside Telegram and in a regular browser.⚠️ Important Note on Localhost: Even when accessing the frontend in a regular desktop browser, do not use http://localhost:5173. Because the application integrates with Telegram, it requires a trusted domain for authentication. Opening localhost will result in a "Bot domain invalid" error. Always use the secure Ngrok HTTPS URL.Backend API Docs (Swagger): http://localhost:8000/docsNgrok Control Panel: http://localhost:4040🛑 Stopping the ApplicationTo stop and remove the containers, run:docker-compose down
