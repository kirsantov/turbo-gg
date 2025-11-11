# Invoice OCR System

A comprehensive Django-based invoice OCR processing system with support for multiple OCR providers (OlmOCR and Marker+DeepSeek R1), built with Django 5, DRF, and django-unfold admin interface.

## Features

- 📄 **Multi-format Support**: Process PDF, JPEG, PNG, and TIFF invoice files
- 🤖 **Dual OCR Providers**:
  - OlmOCR for fast, specialized invoice processing
  - Marker + DeepSeek R1 for advanced AI-powered extraction
- 🏢 **Organization Management**: Group invoices by organization
- 📊 **Structured Data Extraction**: Automatic extraction of:
  - Invoice metadata (number, dates, currency)
  - Supplier and buyer information
  - Line items with quantities, prices, and tax rates
  - Financial totals
- 🎨 **Modern Admin Interface**: Built with django-unfold (Unfold Turbo)
- 🔍 **Advanced Filtering**: Filter invoices by organization, provider, date range
- 📁 **Export Capabilities**: CSV export for invoices
- 🧪 **Comprehensive Testing**: Full test coverage with pytest
- 🔌 **RESTful API**: Complete API with OpenAPI documentation

## Tech Stack

- **Python**: 3.12+
- **Framework**: Django 5.x
- **API**: Django REST Framework (DRF)
- **Database**: PostgreSQL (SQLite for development)
- **Admin UI**: django-unfold
- **Image Processing**: Pillow
- **HTTP Client**: httpx
- **Validation**: Pydantic
- **Testing**: pytest, pytest-django
- **API Docs**: drf-spectacular

## Installation

### Prerequisites

- Python 3.12 or higher
- PostgreSQL (optional, SQLite used by default)
- pip or uv package manager

### Setup Steps

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Install dependencies**

   Using uv (recommended):
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**
   ```bash
   uv run python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   uv run python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   uv run python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1

# OCR Provider (olmocr or marker_deepseek_r1)
OCR_PROVIDER=olmocr

# OlmOCR Configuration
OLMOCR_API_URL=https://api.olmocr.example.com
OLMOCR_API_KEY=your-api-key

# Marker + DeepSeek Configuration
MARKER_API_URL=https://api.marker.example.com
MARKER_API_KEY=your-marker-key
DEEPSEEK_MODEL=r1
```

### Database Setup (PostgreSQL)

For production, configure PostgreSQL:

1. Create database:
   ```sql
   CREATE DATABASE ocrinvoice;
   CREATE USER ocr_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ocrinvoice TO ocr_user;
   ```

2. Update settings:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'ocrinvoice',
           'USER': 'ocr_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

## API Usage

### OCR Invoice Upload

Upload and process an invoice:

```bash
curl -X POST http://localhost:8000/ocr/invoice \
  -F "file=@/path/to/invoice.pdf" \
  -F "organization_name=ACME Medical LLC"
```

Or with existing organization:

```bash
curl -X POST http://localhost:8000/ocr/invoice \
  -F "file=@/path/to/invoice.pdf" \
  -F "organization_id=5"
```

**Response** (201 Created):
```json
{
  "invoice_id": 1,
  "organization_id": 5,
  "number": "INV-2025-00123",
  "issue_date": "2025-11-01",
  "due_date": "2025-11-30",
  "supplier": {
    "name": "ACME Medical LLC",
    "tax_id": "US-12-3456789",
    "address": "123 Market St, SF, CA"
  },
  "buyer": {
    "name": "MediCorp Inc",
    "tax_id": "US-98-7654321",
    "address": "500 Park Ave, NY"
  },
  "currency": "USD",
  "totals": {
    "subtotal": "1200.00",
    "vat": "96.00",
    "total": "1296.00"
  },
  "line_items": [
    {
      "description": "MRI Scan",
      "quantity": "1",
      "unit": "service",
      "unit_price": "1200.00",
      "tax_rate": "8.00",
      "total": "1200.00"
    }
  ],
  "provider_metadata": {
    "name": "olmocr",
    "confidence": 0.93,
    "latency_ms": 1840
  }
}
```

### List Invoices

```bash
# List all invoices
curl http://localhost:8000/api/invoices/

# Filter by organization
curl http://localhost:8000/api/invoices/?organization=5

# Filter by number
curl http://localhost:8000/api/invoices/?number=INV-2025

# Filter by date range
curl http://localhost:8000/api/invoices/?issue_date_from=2025-01-01&issue_date_to=2025-12-31

# Search
curl http://localhost:8000/api/invoices/?search=ACME
```

### Get Invoice Detail

```bash
curl http://localhost:8000/api/invoices/1/
```

### API Documentation

- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Swagger UI**: http://localhost:8000/api/docs/

## Admin Interface

Access the django-unfold admin panel at: http://localhost:8000/admin/

Features:
- **Organizations**: Create and manage organizations
- **Invoices**: View, filter, and export invoices
  - Filter by organization, provider, date range
  - Search by invoice number, supplier, buyer
  - Inline editing of line items
  - CSV export
- **Line Items**: Manage individual line items

## OCR Providers

### OlmOCR

Fast, specialized invoice OCR service.

**Configuration**:
```bash
OCR_PROVIDER=olmocr
OLMOCR_API_URL=https://api.olmocr.example.com
OLMOCR_API_KEY=your-api-key
```

### Marker + DeepSeek R1

Two-step OCR process:
1. Marker converts PDF to structured markdown
2. DeepSeek R1 extracts structured invoice data

**Configuration**:
```bash
OCR_PROVIDER=marker_deepseek_r1
MARKER_API_URL=https://api.marker.example.com
MARKER_API_KEY=your-marker-key
DEEPSEEK_MODEL=r1
```

### Mock Mode

When API URLs are not configured, providers automatically use mock mode for testing:
- Returns sample invoice data
- No external API calls
- Useful for development and testing

## Testing

Run tests with pytest:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=billing

# Run specific test file
uv run pytest billing/tests/test_ocr_endpoint.py

# Run specific test
uv run pytest billing/tests/test_ocr_endpoint.py::TestOCRInvoiceEndpoint::test_upload_invoice_with_organization_name
```

## Code Quality

### Linting

```bash
# Run ruff
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

## Project Structure

```
backend/
├── api/                          # Main Django project
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Main URL configuration
│   └── ...
├── billing/                     # Invoice billing app
│   ├── models.py               # Organization, Invoice, InvoiceLineItem
│   ├── serializers.py          # DRF serializers
│   ├── views.py                # API views
│   ├── admin.py                # django-unfold admin
│   ├── urls.py                 # Billing URLs
│   ├── filters.py              # DRF filters
│   ├── services/               # OCR providers
│   │   ├── ocr_base.py        # Base provider protocol
│   │   ├── ocr_olmocr.py      # OlmOCR implementation
│   │   └── ocr_marker_deepseek.py  # Marker+DeepSeek implementation
│   ├── tests/                  # Test suite
│   │   ├── test_models.py
│   │   ├── test_ocr_endpoint.py
│   │   └── test_ocr_providers.py
│   └── migrations/             # Database migrations
├── media/                       # Uploaded invoice files (gitignored)
├── pyproject.toml              # Project dependencies
├── manage.py                   # Django management script
└── .env.example                # Environment variables template
```

## Database Models

### Organization
- `name` (unique): Organization name
- `tax_id`: Tax identification number
- `address`: Organization address
- Timestamps: `created_at`, `updated_at`

### Invoice
- Foreign key: `organization`
- `number`: Invoice number
- `issue_date`, `due_date`: Invoice dates
- Supplier: `supplier_name`, `supplier_tax_id`, `supplier_address`
- Buyer: `buyer_name`, `buyer_tax_id`, `buyer_address`
- Financial: `currency`, `subtotal_amount`, `vat_amount`, `total_amount`
- OCR: `provider`, `provider_payload`, `raw_text`, `source_file`
- Timestamps: `created_at`, `updated_at`

### InvoiceLineItem
- Foreign key: `invoice`
- `description`: Item description
- `quantity`, `unit`: Quantity and unit of measure
- `unit_price`: Price per unit
- `tax_rate`: Tax rate percentage
- `total`: Line item total

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ocr/invoice` | Upload and OCR invoice |
| GET | `/api/invoices/` | List invoices (paginated) |
| GET | `/api/invoices/{id}/` | Get invoice detail |
| GET | `/api/organizations/` | List organizations |
| GET | `/api/schema/` | OpenAPI schema |
| GET | `/api/docs/` | Swagger UI |
| GET | `/admin/` | Admin interface |

## Security Considerations

- File size limited to 25MB
- Allowed file types: PDF, JPEG, PNG, TIFF
- OCR request timeout: 30 seconds
- No retry logic for failed OCR requests
- All uploads stored in `MEDIA_ROOT`
- Consider S3/cloud storage for production

## Production Deployment

1. **Set environment variables**:
   - `DEBUG=0`
   - `SECRET_KEY` (strong random key)
   - `ALLOWED_HOSTS` (your domain)
   - Database credentials
   - OCR API keys

2. **Configure PostgreSQL**:
   ```bash
   DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname
   ```

3. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Use production server** (gunicorn, uwsgi):
   ```bash
   gunicorn api.wsgi:application --bind 0.0.0.0:8000
   ```

6. **Configure media file storage** (S3, etc.)

## Troubleshooting

### OCR Timeout
- Default timeout: 30 seconds
- Check provider API status
- Verify network connectivity
- Consider increasing timeout for large files

### File Upload Errors
- Verify file size < 25MB
- Check file extension is supported
- Ensure `MEDIA_ROOT` has write permissions

### Database Errors
- Run migrations: `python manage.py migrate`
- Check database connection settings
- Verify database user permissions

## License

This project is part of the turbo-gg repository.

## Support

For issues and questions, please open an issue in the GitHub repository.

---

**Built with Django 5, DRF, and django-unfold**
