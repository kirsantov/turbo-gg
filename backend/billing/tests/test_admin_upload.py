"""Tests for admin OCR upload page."""

from io import BytesIO
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from billing.models import Organization

User = get_user_model()


@pytest.fixture
def admin_client():
    """Create admin client."""
    client = Client()
    user = User.objects.create_superuser(
        username="admin", email="admin@test.com", password="testpass123"
    )
    client.force_login(user)
    return client


@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
xref
0 2
trailer
<<
/Size 2
/Root 1 0 R
>>
startxref
100
%%EOF
"""
    return BytesIO(pdf_content)


@pytest.fixture
def mock_ocr_response():
    """Mock OCR provider response."""
    return {
        "number": "INV-ADMIN-001",
        "issue_date": "2025-11-11",
        "due_date": "2025-12-11",
        "supplier": {
            "name": "Admin Test Supplier",
            "tax_id": "US-99-9999999",
            "address": "123 Admin St",
        },
        "buyer": {
            "name": "Admin Test Buyer",
            "tax_id": "US-88-8888888",
            "address": "456 Admin Ave",
        },
        "currency": "USD",
        "totals": {
            "subtotal": "500.00",
            "vat": "40.00",
            "total": "540.00",
        },
        "line_items": [
            {
                "description": "Admin Test Item",
                "quantity": "1.000",
                "unit": "pc",
                "unit_price": "500.00",
                "tax_rate": "8.00",
                "total": "500.00",
            }
        ],
        "raw_text": "Admin test OCR text",
        "provider_metadata": {
            "name": "olmocr",
            "confidence": 0.97,
            "latency_ms": 1200,
        },
    }


@pytest.mark.django_db
class TestAdminUploadPage:
    """Tests for admin upload invoice page."""

    def test_upload_page_accessible(self, admin_client):
        """Test that upload page is accessible to admin."""
        url = reverse("admin:billing_invoice_upload")
        response = admin_client.get(url)
        assert response.status_code == 200
        assert "Upload Invoice for OCR Processing" in response.content.decode()

    def test_upload_page_requires_login(self):
        """Test that upload page requires authentication."""
        client = Client()
        url = reverse("admin:billing_invoice_upload")
        response = client.get(url)
        # Should redirect to login
        assert response.status_code == 302

    def test_upload_with_new_organization(
        self, admin_client, sample_pdf, mock_ocr_response
    ):
        """Test uploading invoice with new organization via admin."""
        with patch("billing.admin.get_ocr_provider") as mock_provider:
            mock_instance = Mock()
            mock_instance.parse_invoice.return_value = mock_ocr_response
            mock_provider.return_value = mock_instance

            url = reverse("admin:billing_invoice_upload")
            response = admin_client.post(
                url,
                {
                    "file": sample_pdf,
                    "org_type": "new",
                    "organization_name": "New Admin Org",
                    "provider": "olmocr",
                },
            )

            assert response.status_code == 200
            assert Organization.objects.filter(name="New Admin Org").exists()

    def test_upload_with_existing_organization(
        self, admin_client, sample_pdf, mock_ocr_response
    ):
        """Test uploading invoice with existing organization via admin."""
        org = Organization.objects.create(name="Existing Admin Org")

        with patch("billing.admin.get_ocr_provider") as mock_provider:
            mock_instance = Mock()
            mock_instance.parse_invoice.return_value = mock_ocr_response
            mock_provider.return_value = mock_instance

            url = reverse("admin:billing_invoice_upload")
            response = admin_client.post(
                url,
                {
                    "file": sample_pdf,
                    "org_type": "existing",
                    "organization_id": org.id,
                    "provider": "olmocr",
                },
            )

            assert response.status_code == 200
            # Check success message in response
            assert "Successfully processed invoice" in response.content.decode()

    def test_upload_without_file(self, admin_client):
        """Test that upload fails without file."""
        org = Organization.objects.create(name="Test Org")
        url = reverse("admin:billing_invoice_upload")
        response = admin_client.post(
            url,
            {
                "org_type": "existing",
                "organization_id": org.id,
                "provider": "olmocr",
            },
        )

        assert response.status_code == 200
        assert "Please select a file" in response.content.decode()

    def test_upload_without_organization(self, admin_client, sample_pdf):
        """Test that upload fails without organization."""
        url = reverse("admin:billing_invoice_upload")
        response = admin_client.post(
            url,
            {
                "file": sample_pdf,
                "org_type": "existing",
                # No organization_id provided
                "provider": "olmocr",
            },
        )

        assert response.status_code == 200
        assert "Please select an organization" in response.content.decode()
