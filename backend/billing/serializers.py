"""Serializers for billing app."""

from decimal import Decimal

from rest_framework import serializers

from .models import Invoice, InvoiceLineItem, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer."""

    class Meta:
        model = Organization
        fields = ["id", "name", "tax_id", "address", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    """Invoice line item serializer."""

    class Meta:
        model = InvoiceLineItem
        fields = [
            "id",
            "description",
            "quantity",
            "unit",
            "unit_price",
            "tax_rate",
            "total",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    """Invoice serializer with line items."""

    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "organization",
            "organization_name",
            "number",
            "issue_date",
            "due_date",
            "supplier_name",
            "supplier_tax_id",
            "supplier_address",
            "buyer_name",
            "buyer_tax_id",
            "buyer_address",
            "currency",
            "subtotal_amount",
            "vat_amount",
            "total_amount",
            "raw_text",
            "source_file",
            "provider",
            "provider_payload",
            "line_items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class InvoiceUploadSerializer(serializers.Serializer):
    """Serializer for invoice upload and OCR request."""

    file = serializers.FileField(
        help_text="Invoice file (PDF, JPEG, PNG, TIFF). Max 25MB."
    )
    organization_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Existing organization ID",
    )
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        help_text="Organization name (creates if doesn't exist)",
    )

    def validate(self, attrs):
        """Validate that either organization_id or organization_name is provided."""
        org_id = attrs.get("organization_id")
        org_name = attrs.get("organization_name")

        if not org_id and not org_name:
            raise serializers.ValidationError(
                "Either organization_id or organization_name must be provided"
            )

        return attrs

    def validate_file(self, value):
        """Validate file size and type."""
        # Check file size (25 MB max)
        max_size = 25 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size of {max_size // (1024*1024)}MB"
            )

        # Check file extension
        allowed_extensions = ["pdf", "jpg", "jpeg", "png", "tiff", "tif"]
        ext = value.name.split(".")[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type .{ext} not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )

        return value


class InvoiceIngestResultSerializer(serializers.Serializer):
    """Serializer for OCR result response."""

    invoice_id = serializers.IntegerField(help_text="Created invoice ID")
    organization_id = serializers.IntegerField(help_text="Organization ID")
    number = serializers.CharField(help_text="Invoice number")
    issue_date = serializers.DateField(help_text="Invoice issue date")
    due_date = serializers.DateField(
        required=False, allow_null=True, help_text="Invoice due date"
    )

    supplier = serializers.DictField(help_text="Supplier information")
    buyer = serializers.DictField(help_text="Buyer information")

    currency = serializers.CharField(help_text="Currency code")
    totals = serializers.DictField(help_text="Invoice totals")

    line_items = serializers.ListField(
        child=serializers.DictField(), help_text="Invoice line items"
    )

    provider_metadata = serializers.DictField(
        help_text="OCR provider metadata (name, confidence, latency)"
    )
