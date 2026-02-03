# COA Backend

A FastAPI backend service for the COA project with PostgreSQL, Redis, and S3 storage integration.

## Architecture

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Primary database with Alembic migrations
- **Redis** - Caching, session storage, and Celery message broker
- **Celery** - Distributed task queue for background processing
- **Docling** - Document processing library (worker containers only)
- **S3-compatible storage** - File storage service
- **Sentry** - Error monitoring and performance tracking

### Container Architecture

This project uses a multi-container setup to optimize resource usage:

- **API Container** (`Dockerfile.api`) - Lightweight FastAPI service without heavy ML dependencies
- **Worker Container** (`Dockerfile.worker`) - Celery worker with Docling for document processing
- **Support Containers** - Periodic tasks, Beat scheduler use lightweight API image

## Requirements

- Python 3.12+
- Poetry
- Docker & Docker Compose (for local development)

## Quick Start

### Using Docker (Recommended)

1. Copy environment configuration:


```bash
cp .env.sample .env
```

2. Create external volumes and network:
```bash
docker volume create coa_pg_data
docker volume create coa_redis_data
docker volume create coa_build_data
docker network create infuse-network
```

3. Start all services:
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

### Manual Installation

1. Install dependencies:

**For API development (without Docling):**
```bash
# Use API-specific dependencies
cp pyproject.api.toml pyproject.toml
poetry install
poetry shell
```

**For Worker development (with Docling):**
```bash
# Use Worker-specific dependencies
cp pyproject.worker.toml pyproject.toml
poetry install
poetry shell
```

**Before using Docling library:**
- Download required models manually:
  ```bash
  docling-tools models download
  ```
- Set the `ARTIFACTS_PATH` environment variable to specify where models should be stored
- Example: `ARTIFACTS_PATH=/path/to/models` in your `.env` file

2. Set up environment:
```bash
cp .env.sample .env
# Edit .env file with your configuration
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
uvicorn app.main:create_app --factory --reload
```

5. Start Celery worker (in a separate terminal):

**Note:** Contract processing requires Docling library. Use worker dependencies for full functionality.

**For macOS:**
```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES DOCLING_DEVICE=cpu celery -A app.infra.celery.config worker --loglevel=info --concurrency=5 --queues "default,abm_processing,dse_enrichment,abm_sup_file_processing,contract_file_processing,asset_file_processing"```

**For Linux/Windows:**
```bash
celery -A app.infra.celery.config worker --loglevel=info --concurrency=5 --queues "default,abm_processing,dse_enrichment,abm_sup_file_processing,contract_file_processing,asset_file_processing"
```

## Project Structure

```
app/
├── api/                 # API layer
│   └── routers/         # FastAPI routers
├── core/                # Core configurations
│   ├── config/          # Configuration modules
│   └── exc/             # Custom exceptions
├── infra/               # Infrastructure layer
│   ├── database/        # Database connection & migrations
│   └── redis/           # Redis connection
├── models/              # SQLAlchemy models
├── repositories/        # Data access layer
├── schemas/             # Pydantic schemas (DTOs)
├── services/            # Business logic layer
├── uow/                 # Unit of Work pattern
└── utils/               # Utility functions
```

## API Documentation

- **Development**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`
- **Production**: Documentation is disabled for security

## Development

### Code Quality Tools

```bash
# Format code
poetry run ruff format

# Lint code
poetry run ruff check

# Type checking
poetry run mypy .

# Run all checks
./lint.sh
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks before commits:

```bash
poetry run pre-commit install
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade one revision
alembic downgrade -1
```

### Background Tasks with Celery

```bash
# Start Celery worker
poetry run celery -A app.core.celery worker --loglevel=info

# Start Celery Beat scheduler (for periodic tasks)
poetry run celery -A app.core.celery beat --loglevel=info

# Monitor tasks with Flower
poetry run celery -A app.core.celery flower
```

Flower monitoring will be available at `http://localhost:5555`

### Environment Variables

Key environment variables (see `.env.sample` for complete list):

- `SERVER_HOST` - Server host (default: 0.0.0.0)
- `SERVER_PORT` - Server port (default: 8000)
- `EXECUTION_MODE` - PRODUCTION or DEVELOPMENT
- `POSTGRES_*` - Database connection settings
- `REDIS_*` - Redis connection settings
- `S3_*` - S3 storage configuration
- `SENTRY_DSN` - Sentry monitoring URL
- `CELERY_*` - Celery configuration
- `FLOWER_PORT` - Server port (default: 5555)
- `INFUSE_AUTH*` - Auth configuration
- `DSE_BASE_URL` - DSE Service URL
- `ARTIFACTS_PATH` - Path for storing Docling models and artifacts

## Deployment

### Production Deployment

```bash
# Set production environment
export EXECUTION_MODE=PRODUCTION

# Run with production settings
poetry run uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
```

### Docker Production

Update `docker-compose.yaml` for production use:
- Use specific image tags instead of `build`
- Configure proper secrets management
- Set up reverse proxy (nginx/traefik)
- Configure proper logging

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install pre-commit hooks: `poetry run pre-commit install`
4. Make your changes following the existing code style
5. Ensure all tests pass and linting is clean:
   ```bash
   poetry run ruff check
   poetry run ruff format
   poetry run mypy .
   ```
6. Run database migrations if you modified models
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

## Documentation

[See the campaign creation flow](doc/campaign_creation_doc.md)

## License

This project is proprietary software. All rights reserved.
