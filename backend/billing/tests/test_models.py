"""Tests for billing models."""

from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from billing.models import Invoice, InvoiceLineItem, Organization


@pytest.mark.django_db
class TestOrganization:
    """Tests for Organization model."""

    def test_create_organization(self):
        """Test creating an organization."""
        org = Organization.objects.create(
            name="Test Corp",
            tax_id="US-12-3456789",
            address="123 Test St",
        )
        assert org.name == "Test Corp"
        assert org.tax_id == "US-12-3456789"
        assert str(org) == "Test Corp"

    def test_organization_unique_name(self):
        """Test that organization names must be unique."""
        Organization.objects.create(name="Test Corp")
        with pytest.raises(Exception):  # IntegrityError
            Organization.objects.create(name="Test Corp")


@pytest.mark.django_db
class TestInvoice:
    """Tests for Invoice model."""

    def test_create_invoice(self):
        """Test creating an invoice."""
        org = Organization.objects.create(name="Test Corp")
        invoice = Invoice.objects.create(
            organization=org,
            number="INV-001",
            issue_date="2025-11-11",
            supplier_name="Supplier Inc",
            buyer_name="Buyer LLC",
            currency="USD",
            subtotal_amount=Decimal("100.00"),
            vat_amount=Decimal("8.00"),
            total_amount=Decimal("108.00"),
            provider="olmocr",
        )
        assert invoice.number == "INV-001"
        assert invoice.total_amount == Decimal("108.00")
        assert str(invoice) == "INV-001 - Test Corp"


@pytest.mark.django_db
class TestInvoiceLineItem:
    """Tests for InvoiceLineItem model."""

    def test_create_line_item(self):
        """Test creating an invoice line item."""
        org = Organization.objects.create(name="Test Corp")
        invoice = Invoice.objects.create(
            organization=org,
            number="INV-001",
            issue_date="2025-11-11",
            supplier_name="Supplier Inc",
            buyer_name="Buyer LLC",
            provider="olmocr",
        )
        line_item = InvoiceLineItem.objects.create(
            invoice=invoice,
            description="Test Item",
            quantity=Decimal("2.000"),
            unit="pcs",
            unit_price=Decimal("50.00"),
            total=Decimal("100.00"),
        )
        assert line_item.description == "Test Item"
        assert line_item.quantity == Decimal("2.000")
        assert line_item.total == Decimal("100.00")
