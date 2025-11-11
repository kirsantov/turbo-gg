"""Tests for OCR invoice endpoint."""

import os
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from billing.models import Invoice, InvoiceLineItem, Organization


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    # Create a minimal PDF
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Invoice) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF
"""
    return SimpleUploadedFile(
        "test_invoice.pdf",
        pdf_content,
        content_type="application/pdf",
    )


@pytest.fixture
def mock_ocr_response():
    """Mock OCR provider response."""
    return {
        "number": "INV-2025-TEST-001",
        "issue_date": "2025-11-11",
        "due_date": "2025-12-11",
        "supplier": {
            "name": "Test Supplier LLC",
            "tax_id": "US-11-1111111",
            "address": "123 Test St, Test City, TC 12345",
        },
        "buyer": {
            "name": "Test Buyer Inc",
            "tax_id": "US-22-2222222",
            "address": "456 Buyer Ave, Test Town, TT 67890",
        },
        "currency": "USD",
        "totals": {
            "subtotal": "1000.00",
            "vat": "80.00",
            "total": "1080.00",
        },
        "line_items": [
            {
                "description": "Test Service",
                "quantity": "2.000",
                "unit": "hours",
                "unit_price": "500.00",
                "tax_rate": "8.00",
                "total": "1000.00",
            }
        ],
        "raw_text": "Test OCR extracted text",
        "provider_metadata": {
            "name": "olmocr",
            "confidence": 0.95,
            "latency_ms": 1500,
        },
    }


@pytest.mark.django_db
class TestOCRInvoiceEndpoint:
    """Tests for OCR invoice upload endpoint."""

    def test_upload_invoice_with_organization_name(
        self, api_client, sample_pdf, mock_ocr_response
    ):
        """Test uploading invoice with organization_name."""
        with patch("billing.views.get_ocr_provider") as mock_provider:
            # Mock the OCR provider
            mock_instance = Mock()
            mock_instance.parse_invoice.return_value = mock_ocr_response
            mock_provider.return_value = mock_instance

            # Upload invoice
            response = api_client.post(
                "/ocr/invoice",
                {
                    "file": sample_pdf,
                    "organization_name": "Test Organization",
                },
                format="multipart",
            )

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "invoice_id" in data
        assert "organization_id" in data
        assert data["number"] == "INV-2025-TEST-001"
        assert data["currency"] == "USD"
        assert data["totals"]["total"] == "1080.00"
        assert len(data["line_items"]) == 1

        # Check database records
        assert Invoice.objects.count() == 1
        assert InvoiceLineItem.objects.count() == 1
        assert Organization.objects.count() == 1

        invoice = Invoice.objects.first()
        assert invoice.number == "INV-2025-TEST-001"
        assert invoice.total_amount == Decimal("1080.00")
        assert invoice.organization.name == "Test Organization"

    def test_upload_invoice_with_organization_id(
        self, api_client, sample_pdf, mock_ocr_response
    ):
        """Test uploading invoice with existing organization_id."""
        # Create organization first
        org = Organization.objects.create(name="Existing Org")

        with patch("billing.views.get_ocr_provider") as mock_provider:
            mock_instance = Mock()
            mock_instance.parse_invoice.return_value = mock_ocr_response
            mock_provider.return_value = mock_instance

            response = api_client.post(
                "/ocr/invoice",
                {
                    "file": sample_pdf,
                    "organization_id": org.id,
                },
                format="multipart",
            )

        assert response.status_code == 201
        data = response.json()
        assert data["organization_id"] == org.id

        invoice = Invoice.objects.first()
        assert invoice.organization == org

    def test_upload_invoice_missing_organization(self, api_client, sample_pdf):
        """Test that upload fails without organization info."""
        response = api_client.post(
            "/ocr/invoice",
            {"file": sample_pdf},
            format="multipart",
        )
        assert response.status_code == 400

    def test_upload_invoice_invalid_organization_id(self, api_client, sample_pdf):
        """Test that upload fails with invalid organization_id."""
        response = api_client.post(
            "/ocr/invoice",
            {
                "file": sample_pdf,
                "organization_id": 9999,
            },
            format="multipart",
        )
        assert response.status_code == 400

    def test_upload_invoice_ocr_timeout(self, api_client, sample_pdf):
        """Test handling of OCR timeout."""
        with patch("billing.views.get_ocr_provider") as mock_provider:
            mock_instance = Mock()
            mock_instance.parse_invoice.side_effect = TimeoutError("OCR timeout")
            mock_provider.return_value = mock_instance

            response = api_client.post(
                "/ocr/invoice",
                {
                    "file": sample_pdf,
                    "organization_name": "Test Org",
                },
                format="multipart",
            )

        assert response.status_code == 504

    def test_upload_invoice_ocr_error(self, api_client, sample_pdf):
        """Test handling of OCR processing error."""
        with patch("billing.views.get_ocr_provider") as mock_provider:
            mock_instance = Mock()
            mock_instance.parse_invoice.side_effect = ValueError("Invalid PDF")
            mock_provider.return_value = mock_instance

            response = api_client.post(
                "/ocr/invoice",
                {
                    "file": sample_pdf,
                    "organization_name": "Test Org",
                },
                format="multipart",
            )

        assert response.status_code == 422


@pytest.mark.django_db
class TestInvoiceListAPI:
    """Tests for invoice list API."""

    def test_list_invoices(self, api_client):
        """Test listing invoices."""
        org = Organization.objects.create(name="Test Org")
        Invoice.objects.create(
            organization=org,
            number="INV-001",
            issue_date="2025-11-01",
            supplier_name="Supplier 1",
            buyer_name="Buyer 1",
            provider="olmocr",
        )
        Invoice.objects.create(
            organization=org,
            number="INV-002",
            issue_date="2025-11-02",
            supplier_name="Supplier 2",
            buyer_name="Buyer 2",
            provider="marker_deepseek_r1",
        )

        response = api_client.get("/api/invoices/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    def test_filter_invoices_by_organization(self, api_client):
        """Test filtering invoices by organization."""
        org1 = Organization.objects.create(name="Org 1")
        org2 = Organization.objects.create(name="Org 2")

        Invoice.objects.create(
            organization=org1,
            number="INV-001",
            issue_date="2025-11-01",
            supplier_name="Supplier 1",
            buyer_name="Buyer 1",
            provider="olmocr",
        )
        Invoice.objects.create(
            organization=org2,
            number="INV-002",
            issue_date="2025-11-02",
            supplier_name="Supplier 2",
            buyer_name="Buyer 2",
            provider="olmocr",
        )

        response = api_client.get(f"/api/invoices/?organization={org1.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["number"] == "INV-001"

    def test_search_invoices(self, api_client):
        """Test searching invoices."""
        org = Organization.objects.create(name="Test Org")
        Invoice.objects.create(
            organization=org,
            number="INV-UNIQUE-001",
            issue_date="2025-11-01",
            supplier_name="Special Supplier",
            buyer_name="Buyer 1",
            provider="olmocr",
        )
        Invoice.objects.create(
            organization=org,
            number="INV-002",
            issue_date="2025-11-02",
            supplier_name="Regular Supplier",
            buyer_name="Buyer 2",
            provider="olmocr",
        )

        response = api_client.get("/api/invoices/?search=UNIQUE")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["number"] == "INV-UNIQUE-001"

    def test_get_invoice_detail(self, api_client):
        """Test getting invoice detail."""
        org = Organization.objects.create(name="Test Org")
        invoice = Invoice.objects.create(
            organization=org,
            number="INV-001",
            issue_date="2025-11-01",
            supplier_name="Supplier 1",
            buyer_name="Buyer 1",
            provider="olmocr",
        )
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description="Test Item",
            quantity=Decimal("1.000"),
            unit_price=Decimal("100.00"),
            total=Decimal("100.00"),
        )

        response = api_client.get(f"/api/invoices/{invoice.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["number"] == "INV-001"
        assert len(data["line_items"]) == 1
