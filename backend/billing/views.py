"""API views for billing app."""

import logging
from decimal import Decimal

from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import InvoiceFilter
from .models import Invoice, InvoiceLineItem, Organization
from .serializers import (
    InvoiceIngestResultSerializer,
    InvoiceSerializer,
    InvoiceUploadSerializer,
    OrganizationSerializer,
)
from .services import get_ocr_provider

logger = logging.getLogger(__name__)


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Organization model."""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "tax_id"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model."""

    queryset = Invoice.objects.select_related("organization").prefetch_related(
        "line_items"
    )
    serializer_class = InvoiceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InvoiceFilter
    search_fields = ["number", "supplier_name", "buyer_name"]
    ordering_fields = ["issue_date", "total_amount", "created_at"]
    ordering = ["-created_at"]


@extend_schema(
    request=InvoiceUploadSerializer,
    responses={201: InvoiceIngestResultSerializer},
    examples=[
        OpenApiExample(
            "Invoice Upload Example",
            value={
                "file": "binary",
                "organization_name": "ACME Medical LLC",
            },
            request_only=True,
        ),
        OpenApiExample(
            "OCR Result Example",
            value={
                "invoice_id": 1,
                "organization_id": 5,
                "number": "INV-2025-00123",
                "issue_date": "2025-11-01",
                "due_date": "2025-11-30",
                "supplier": {
                    "name": "ACME Medical LLC",
                    "tax_id": "US-12-3456789",
                    "address": "123 Market St, SF, CA",
                },
                "buyer": {
                    "name": "MediCorp Inc",
                    "tax_id": "US-98-7654321",
                    "address": "500 Park Ave, NY",
                },
                "currency": "USD",
                "totals": {"subtotal": "1200.00", "vat": "96.00", "total": "1296.00"},
                "line_items": [
                    {
                        "description": "MRI Scan",
                        "quantity": "1",
                        "unit": "service",
                        "unit_price": "1200.00",
                        "tax_rate": "8.00",
                        "total": "1200.00",
                    }
                ],
                "provider_metadata": {
                    "name": "olmocr",
                    "confidence": 0.93,
                    "latency_ms": 1840,
                },
            },
            response_only=True,
        ),
    ],
)
@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([AllowAny])
def ocr_invoice_upload(request):
    """
    Upload and OCR an invoice.

    Accepts a file upload (PDF/image) and performs OCR extraction
    using the configured provider (olmocr or marker_deepseek_r1).

    Returns structured invoice data and saves to database.
    """
    serializer = InvoiceUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    file = serializer.validated_data["file"]
    org_id = serializer.validated_data.get("organization_id")
    org_name = serializer.validated_data.get("organization_name")

    # Get or create organization
    if org_id:
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(
                {"error": f"Organization with id={org_id} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    elif org_name:
        organization, _ = Organization.objects.get_or_create(name=org_name)
    else:
        return Response(
            {"error": "Either organization_id or organization_name required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get OCR provider
    provider_name = getattr(settings, "OCR_PROVIDER", "olmocr")
    try:
        provider = get_ocr_provider(provider_name)
    except ValueError as e:
        logger.error(f"Invalid OCR provider: {e}")
        return Response(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Perform OCR
    try:
        normalized_data = provider.parse_invoice(file.file)
    except TimeoutError as e:
        logger.error(f"OCR timeout: {e}")
        return Response(
            {"error": "OCR request timed out"}, status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return Response(
            {"error": f"Failed to process invoice: {str(e)}"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # Create Invoice
    try:
        invoice = Invoice.objects.create(
            organization=organization,
            number=normalized_data.get("number", ""),
            issue_date=normalized_data.get("issue_date"),
            due_date=normalized_data.get("due_date"),
            supplier_name=normalized_data.get("supplier", {}).get("name", ""),
            supplier_tax_id=normalized_data.get("supplier", {}).get("tax_id"),
            supplier_address=normalized_data.get("supplier", {}).get("address"),
            buyer_name=normalized_data.get("buyer", {}).get("name", ""),
            buyer_tax_id=normalized_data.get("buyer", {}).get("tax_id"),
            buyer_address=normalized_data.get("buyer", {}).get("address"),
            currency=normalized_data.get("currency", "USD"),
            subtotal_amount=Decimal(normalized_data.get("totals", {}).get("subtotal", "0")),
            vat_amount=Decimal(normalized_data.get("totals", {}).get("vat", "0")),
            total_amount=Decimal(normalized_data.get("totals", {}).get("total", "0")),
            raw_text=normalized_data.get("raw_text", ""),
            source_file=file,
            provider=provider_name,
            provider_payload=normalized_data.get("provider_metadata", {}),
        )

        # Create line items
        for item_data in normalized_data.get("line_items", []):
            InvoiceLineItem.objects.create(
                invoice=invoice,
                description=item_data.get("description", ""),
                quantity=Decimal(item_data.get("quantity", "1")),
                unit=item_data.get("unit"),
                unit_price=Decimal(item_data.get("unit_price", "0")),
                tax_rate=Decimal(item_data.get("tax_rate", "0"))
                if item_data.get("tax_rate")
                else None,
                total=Decimal(item_data.get("total", "0")),
            )

    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        return Response(
            {"error": f"Failed to save invoice: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Prepare response
    response_data = {
        "invoice_id": invoice.id,
        "organization_id": organization.id,
        "number": invoice.number,
        "issue_date": invoice.issue_date,
        "due_date": invoice.due_date,
        "supplier": {
            "name": invoice.supplier_name,
            "tax_id": invoice.supplier_tax_id,
            "address": invoice.supplier_address,
        },
        "buyer": {
            "name": invoice.buyer_name,
            "tax_id": invoice.buyer_tax_id,
            "address": invoice.buyer_address,
        },
        "currency": invoice.currency,
        "totals": {
            "subtotal": str(invoice.subtotal_amount),
            "vat": str(invoice.vat_amount),
            "total": str(invoice.total_amount),
        },
        "line_items": [
            {
                "description": item.description,
                "quantity": str(item.quantity),
                "unit": item.unit,
                "unit_price": str(item.unit_price),
                "tax_rate": str(item.tax_rate) if item.tax_rate else None,
                "total": str(item.total),
            }
            for item in invoice.line_items.all()
        ],
        "provider_metadata": normalized_data.get("provider_metadata", {}),
    }

    logger.info(
        f"Successfully processed invoice {invoice.number} (ID: {invoice.id}) "
        f"for organization {organization.name}"
    )

    return Response(response_data, status=status.HTTP_201_CREATED)
