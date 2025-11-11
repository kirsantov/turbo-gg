from decimal import Decimal

from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.db import models


class Organization(models.Model):
    """Organization entity for grouping invoices."""

    name = models.CharField(max_length=255, unique=True, db_index=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organizations"
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


class Invoice(models.Model):
    """Invoice model storing OCR-extracted invoice data."""

    PROVIDER_CHOICES = [
        ("olmocr", "OlmOCR"),
        ("marker_deepseek_r1", "Marker + DeepSeek R1"),
    ]

    # Relations
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invoices",
        db_index=True,
    )

    # Invoice fields
    number = models.CharField(max_length=100, db_index=True)
    issue_date = models.DateField(db_index=True)
    due_date = models.DateField(blank=True, null=True)

    # Supplier info
    supplier_name = models.CharField(max_length=255)
    supplier_tax_id = models.CharField(max_length=100, blank=True, null=True)
    supplier_address = models.TextField(blank=True, null=True)

    # Buyer info
    buyer_name = models.CharField(max_length=255)
    buyer_tax_id = models.CharField(max_length=100, blank=True, null=True)
    buyer_address = models.TextField(blank=True, null=True)

    # Financial
    currency = models.CharField(max_length=3, default="USD")
    subtotal_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    vat_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"), db_index=True
    )

    # OCR data
    raw_text = models.TextField(blank=True, null=True, help_text="Raw OCR text")
    source_file = models.FileField(
        upload_to="invoices/%Y/%m/%d/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "jpg", "jpeg", "png", "tiff", "tif"]
            ),
            MaxValueValidator(25 * 1024 * 1024),  # 25 MB
        ],
    )
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, db_index=True)
    provider_payload = models.JSONField(
        default=dict, blank=True, help_text="Raw OCR provider response"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoices"
        ordering = ["-created_at"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=["organization", "issue_date"]),
            models.Index(fields=["number", "organization"]),
        ]

    def __str__(self):
        return f"{self.number} - {self.organization.name}"


class InvoiceLineItem(models.Model):
    """Line items for invoices."""

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="line_items"
    )
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal("1"))
    unit = models.CharField(max_length=50, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "invoice_line_items"
        ordering = ["id"]
        verbose_name = "Invoice Line Item"
        verbose_name_plural = "Invoice Line Items"

    def __str__(self):
        return f"{self.invoice.number} - {self.description[:50]}"
