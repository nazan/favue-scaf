# favue-scaf

FastAPI + Vue.js Project Scaffolding Tool

A Docker-based tool that generates a complete development environment for FastAPI backend and Vue.js frontend applications with Docker orchestration, git submodules, and out-of-the-box functionality.

## Features

- **Docker-Based**: Run in a container, no Python installation needed on host
- **Interactive CLI**: Prompts for project configuration
- **Git Submodules**: Automatically sets up backend and frontend as separate git repositories
- **Docker Orchestration**: Complete docker-compose setup with MySQL database
- **Service Layer Architecture**: FastAPI backend with dependency injection and service layer separation
- **Hot Reload**: Both backend and frontend support hot reloading
- **Testing Setup**: Pytest configuration with example test
- **Database Migrations**: Alembic setup ready to use
- **Out-of-the-Box**: Generated project runs with a single `make setup` command

## Building the Docker Image

### Prerequisites

- Docker
- Git
- Make (optional, but recommended)

### Build Steps

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd favue-scaf
   ```

2. Build the Docker image:
   ```bash
   make build
   ```
   
   Or manually:
   ```bash
   docker build -t favue-scaf .
   ```

This creates a Docker image named `favue-scaf` containing the scaffolding tool and all templates.

## Using the Tool

### Quick Start

1. Ensure Docker is running on your system

2. Run the scaffolder:
   ```bash
   make run
   ```
   
   This will:
   - Build the Docker image (if not already built)
   - Mount your `~/projects` directory into the container
   - Run the interactive scaffolder
   - Create the new project in your projects folder

3. Follow the interactive prompts:
   - **Project name** (e.g., `myapp`)
   - **Project location** (defaults to `/workspace/myapp` which maps to `~/projects/myapp` on your host)
   - **Database name** (defaults to project name)
   - **Port numbers** (API, Web, Database - defaults: 8000, 5173, 3306)

4. After scaffolding, navigate to your new project and run:
   ```bash
   cd ~/projects/your-project-name
   make setup
   ```

### Customizing the Projects Directory

You can override the default projects directory (`~/projects`) by setting the `PROJECTS_DIR` environment variable:

```bash
export PROJECTS_DIR=/custom/path/to/projects
make run
```

Or inline:
```bash
PROJECTS_DIR=/custom/path/to/projects make run
```

### Manual Docker Run

If you prefer to run Docker directly without Make:

```bash
docker run --rm -it \
  -e USER_ID=$(id -u) \
  -e GROUP_ID=$(id -g) \
  -v "$HOME/projects:/workspace" \
  -w /workspace \
  favue-scaf \
  python -m scaffolder
```

**Note:** The `USER_ID` and `GROUP_ID` environment variables ensure files are created with your host user's ownership.

### Custom Mount Point

To use a different directory, adjust the mount:
```bash
docker run --rm -it \
  -e USER_ID=$(id -u) \
  -e GROUP_ID=$(id -g) \
  -v "/path/to/your/projects:/workspace" \
  -w /workspace \
  favue-scaf \
  python -m scaffolder
```

## Generated Project Structure

```
your-project-name/
├── compose.yml          # Docker Compose configuration
├── Makefile            # Development commands
├── .env.example        # Environment variables template
├── README.md           # Project documentation
├── your-project-core/  # FastAPI backend (git submodule)
│   ├── app/
│   │   ├── api/        # API routes
│   │   ├── core/       # DI container
│   │   ├── db/         # Database session and tables
│   │   ├── services/   # Business logic layer
│   │   └── schemas/    # Pydantic models
│   ├── alembic/        # Database migrations
│   └── tests/          # Test suite
└── your-project-web/   # Vue.js frontend (git submodule)
    └── src/
        ├── router/      # Vue Router
        ├── services/    # API client
        └── views/       # Vue components
```

## Generated Project Features

### Backend (FastAPI)

- **Service Layer**: Business logic separated from framework
- **Dependency Injection**: IoC container with singleton and scoped lifetimes
- **SQLAlchemy Core**: Async database access without ORM
- **Alembic**: Database migration system
- **Pytest**: Testing framework with async support
- **Example Service**: `UtilityService` with database version query
- **Example Endpoint**: `GET /api/dbversion` demonstrating end-to-end connectivity
- **Pydantic Models**: Example request/response schemas

### Frontend (Vue.js)

- **Vue 3**: Composition API
- **Vue Router**: Client-side routing
- **Vite**: Fast development server with HMR
- **API Client**: Centralized API service with error handling
- **Example View**: Home page calling `/api/dbversion` endpoint

### Development Environment

- **Docker Compose**: All services orchestrated
- **Hot Reload**: Both backend and frontend auto-reload on changes
- **Makefile**: Common development tasks
- **Volume Management**: Persistent database storage

## Generated Project Usage

After scaffolding, navigate to your project and use the Makefile:

### Setup (First Time)

```bash
cd ~/projects/your-project-name
make setup
```

This will:
1. Create `.env` files from examples
2. Create Docker volumes
3. Build Docker images
4. Install Python dependencies
5. Install npm dependencies
6. Start all services
7. Run database migrations

### Common Makefile Commands

- `make setup` - Complete setup (first time only)
- `make build` - Build Docker images
- `make pip` - Install Python dependencies into persistent volume
- `make npm` - Install npm dependencies
- `make up` - Start all services (backend, frontend, database)
- `make down` - Stop all services
- `make migrate` - Run database migrations
- `make test` - Run backend tests
- `make logs` - View service logs

### Accessing Services

After running `make setup` or `make up`:

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:3306 (default port, configurable)

## Development

This project itself is a living project. As you discover improvements or issues with the scaffolding process, you can:

1. Modify templates in `templates/` directory
2. Update the main script in `scaffolder/__main__.py`
3. Rebuild the Docker image: `make build`
4. Test locally: `make run`

### Running Locally (Without Docker)

For development, you can also run the scaffolder directly:

```bash
python -m scaffolder
```

Make sure you're in the project root directory so it can find the `templates/` folder.

## Requirements

**For using this scaffolder:**
- Docker
- Git

**For the generated projects:**
- Docker and Docker Compose
- Git
- Linux/macOS (WSL2 on Windows)

## License

MIT
