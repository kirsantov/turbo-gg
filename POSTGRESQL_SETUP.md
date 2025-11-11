# PostgreSQL Setup

## Current Status

**Currently using**: SQLite (`db.sqlite3`) for quick development
**Production ready**: PostgreSQL configuration is ready, just needs to be activated

## Why SQLite Now?

- ✅ Zero setup - works immediately
- ✅ Single file database (easy backup)
- ✅ Perfect for development and testing
- ✅ Good for small production (< 100k invoices)

## Why Switch to PostgreSQL?

PostgreSQL is better for production because:
- 🚀 Better performance with large datasets
- 🔒 Better concurrency (multiple users)
- 📊 Advanced indexing and querying
- 🛡️ Better data integrity and ACID compliance
- 📈 Scales better (millions of invoices)

## How to Switch to PostgreSQL

### Option 1: Using Docker Compose (Recommended)

The project already has PostgreSQL configured in `docker-compose.yaml`:

```bash
# Start all services including PostgreSQL
docker compose up

# PostgreSQL will be available at:
# Host: localhost
# Port: 5434 (external), 5432 (internal)
# Database: db
# User: postgres
# Password: change-password
```

No code changes needed - `docker-compose.yaml` already has the right environment variables!

### Option 2: Install PostgreSQL Locally

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo service postgresql start

# Create database and user
sudo -u postgres psql
CREATE DATABASE db;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE db TO myuser;
\q

# Update .env.backend:
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=db
DATABASE_USER=myuser
DATABASE_PASSWORD=mypassword

# Run migrations
cd backend
uv run python manage.py migrate

# Restart backend
uv run python manage.py runserver
```

### Option 3: Use Managed PostgreSQL (Cloud)

For production, use managed PostgreSQL:
- **AWS RDS**: https://aws.amazon.com/rds/postgresql/
- **Google Cloud SQL**: https://cloud.google.com/sql/postgresql
- **DigitalOcean**: https://www.digitalocean.com/products/managed-databases-postgresql
- **Heroku**: https://www.heroku.com/postgres
- **Supabase**: https://supabase.com/ (Free tier available!)

Update `.env.backend` with connection details from your provider.

## Configuration

### Current Setup

```bash
# .env.backend
# USE_SQLITE=true    # Uncomment to force SQLite
DATABASE_NAME=db
DATABASE_USER=postgres
DATABASE_PASSWORD=change-password
DATABASE_HOST=localhost
DATABASE_PORT=5434
```

### Switch Back to SQLite

If you want to use SQLite temporarily:

```bash
# In .env.backend, add:
USE_SQLITE=true

# Restart backend
```

## Migrating Data from SQLite to PostgreSQL

If you have data in SQLite and want to move to PostgreSQL:

```bash
# 1. Dump SQLite data
cd backend
uv run python manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission -e sessions \
  --indent 2 -o data_dump.json

# 2. Switch to PostgreSQL (comment out USE_SQLITE in .env.backend)

# 3. Run migrations on PostgreSQL
uv run python manage.py migrate

# 4. Load data
uv run python manage.py loaddata data_dump.json

# 5. Verify
uv run python manage.py shell
>>> from billing.models import Invoice
>>> Invoice.objects.count()
```

## Checking Current Database

```bash
cd backend
uv run python manage.py shell

# Check which database is being used:
from django.conf import settings
print(settings.DATABASES['default']['ENGINE'])

# If you see 'postgresql': ✅ Using PostgreSQL
# If you see 'sqlite3': ℹ️ Using SQLite
```

## Performance Comparison

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Setup time | Instant | 5-10 min |
| Concurrent writes | Single | Unlimited |
| Max practical size | ~1GB | ~TB+ |
| Backup | Copy file | pg_dump |
| Replication | No | Yes |
| Full-text search | Basic | Advanced |
| JSON queries | Limited | Excellent |

## Recommendation

- **Development**: SQLite is fine (current setup)
- **Small production** (< 1000 invoices/month): SQLite works well
- **Medium/Large production**: Use PostgreSQL
- **Multiple servers**: Use PostgreSQL

## Troubleshooting

### "relation does not exist" error

```bash
# Run migrations
cd backend
uv run python manage.py migrate
```

### Connection refused

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5434

# If not running:
# Docker: docker compose up db
# Local: sudo service postgresql start
```

### Authentication failed

Check credentials in `.env.backend` match your PostgreSQL setup.

---

**Current Status**: Using SQLite, ready to switch to PostgreSQL anytime!
