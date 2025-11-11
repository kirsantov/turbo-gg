# Quick Start Guide

## 🚀 Start the Project

```bash
docker compose up
```

Wait for all services to start (30-60 seconds).

## 🌐 Access Points

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **Django Admin**: http://localhost:8001/admin/
- **API Docs (Swagger)**: http://localhost:8001/api/docs/
- **API Schema**: http://localhost:8001/api/schema/

## 🔑 Login Credentials

### Admin User
- Username: `admin`
- Password: `admin`

### Test User
- Username: `testuser`
- Password: `testpass123`

## 📝 Common Commands

### Backend (Django)
```bash
# Run migrations
docker compose exec api uv run -- python manage.py migrate

# Create superuser
docker compose exec api uv run -- python manage.py createsuperuser

# Django shell
docker compose exec api uv run -- python manage.py shell

# Run tests
docker compose exec api uv run -- pytest .
```

### Frontend (Next.js)
```bash
# Regenerate TypeScript API client (after backend changes)
docker compose exec web pnpm openapi:generate

# Install new package
docker compose exec web pnpm --filter web add <package-name>

# Install workspace-wide package
docker compose exec web pnpm add <package-name> -w
```

### Docker
```bash
# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild containers
docker compose up --build
```

## 🔄 Development Workflow

1. **Make backend changes** (Django models, views, serializers)
2. **Regenerate types**: `docker compose exec web pnpm openapi:generate`
3. **Use types in frontend** - they're automatically available in `@frontend/types`

## 🤖 OCR Configuration

By default, the system runs in **mock mode** (returns fake invoice data for testing).

To use real OCR:
- See **OCR_SETUP.md** for detailed setup instructions
- Quick options:
  - **OlmOCR**: Self-hosted, free, good accuracy (requires GPU)
  - **Marker + DeepSeek R1**: Cloud-based, ~$0.01/invoice, very accurate

Current status: **Mock mode** (no API keys configured)

## 📚 More Info

- See **OCR_SETUP.md** for OCR provider configuration
- See **CLAUDE.md** for complete architecture documentation
- See **README.md** for detailed feature list
- Raise issues at: https://github.com/unfoldadmin/turbo/issues

## ⚠️ Note on Ports

This setup uses custom ports to avoid conflicts:
- PostgreSQL: **5434** (not 5432)
- API: **8001** (not 8000)
- Frontend: **3001** (not 3000)
