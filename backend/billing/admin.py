"""Admin configuration for billing app with django-unfold."""

import csv
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import Invoice, InvoiceLineItem, Organization
from .services import get_ocr_provider

logger = logging.getLogger(__name__)


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    """Admin for Organization model."""

    list_display = ["name", "tax_id", "invoice_count", "created_at"]
    search_fields = ["name", "tax_id"]
    list_filter = ["created_at"]
    ordering = ["name"]

    fieldsets = (
        (
            "Organization Information",
            {
                "fields": ("name", "tax_id", "address"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at"]

    def invoice_count(self, obj):
        """Display number of invoices for this organization."""
        count = obj.invoices.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)

    invoice_count.short_description = "Invoices"


class InvoiceLineItemInline(TabularInline):
    """Inline admin for InvoiceLineItem."""

    model = InvoiceLineItem
    extra = 0
    fields = ["description", "quantity", "unit", "unit_price", "tax_rate", "total"]

    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly if invoice exists."""
        if obj:  # Editing existing invoice
            return []
        return []


@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    """Admin for Invoice model."""

    list_display = [
        "number",
        "organization",
        "issue_date",
        "total_amount_display",
        "currency",
        "provider_badge",
        "created_at",
    ]
    list_filter = [
        "organization",
        "provider",
        "issue_date",
        "created_at",
        "currency",
    ]
    search_fields = ["number", "supplier_name", "buyer_name", "organization__name"]
    date_hierarchy = "issue_date"
    ordering = ["-created_at"]

    inlines = [InvoiceLineItemInline]

    fieldsets = (
        (
            "Invoice Information",
            {
                "fields": (
                    "organization",
                    "number",
                    "issue_date",
                    "due_date",
                    "currency",
                ),
            },
        ),
        (
            "Supplier Information",
            {
                "fields": ("supplier_name", "supplier_tax_id", "supplier_address"),
            },
        ),
        (
            "Buyer Information",
            {
                "fields": ("buyer_name", "buyer_tax_id", "buyer_address"),
            },
        ),
        (
            "Financial Details",
            {
                "fields": ("subtotal_amount", "vat_amount", "total_amount"),
            },
        ),
        (
            "OCR Data",
            {
                "fields": ("source_file", "provider", "raw_text", "provider_payload"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at"]

    actions = ["export_as_csv"]

    def get_urls(self):
        """Add custom URLs for upload page."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(self.upload_invoice_view),
                name="billing_invoice_upload",
            ),
        ]
        return custom_urls + urls

    def upload_invoice_view(self, request):
        """Custom view for uploading and processing invoices with OCR."""
        context = {
            **self.admin_site.each_context(request),
            "title": "Upload Invoice for OCR",
            "organizations": Organization.objects.all().order_by("name"),
            "current_provider": getattr(settings, "OCR_PROVIDER", "olmocr"),
        }

        if request.method == "POST":
            try:
                # Get form data
                file = request.FILES.get("file")
                org_type = request.POST.get("org_type")
                provider_name = request.POST.get("provider", settings.OCR_PROVIDER)

                if not file:
                    messages.error(request, "Please select a file to upload.")
                    return render(
                        request, "admin/billing/upload_invoice.html", context
                    )

                # Get or create organization
                if org_type == "existing":
                    org_id = request.POST.get("organization_id")
                    if not org_id:
                        messages.error(request, "Please select an organization.")
                        return render(
                            request, "admin/billing/upload_invoice.html", context
                        )
                    try:
                        organization = Organization.objects.get(id=org_id)
                    except Organization.DoesNotExist:
                        messages.error(request, "Selected organization not found.")
                        return render(
                            request, "admin/billing/upload_invoice.html", context
                        )
                else:  # new
                    org_name = request.POST.get("organization_name")
                    if not org_name:
                        messages.error(request, "Please enter an organization name.")
                        return render(
                            request, "admin/billing/upload_invoice.html", context
                        )
                    organization, created = Organization.objects.get_or_create(
                        name=org_name
                    )
                    if created:
                        messages.success(
                            request, f"Created new organization: {org_name}"
                        )

                # Get OCR provider
                try:
                    provider = get_ocr_provider(provider_name)
                except ValueError as e:
                    messages.error(request, f"Invalid OCR provider: {e}")
                    return render(
                        request, "admin/billing/upload_invoice.html", context
                    )

                # Process with OCR
                try:
                    normalized_data = provider.parse_invoice(file.file)
                except TimeoutError:
                    messages.error(
                        request,
                        "OCR processing timed out. Please try again with a smaller file.",
                    )
                    return render(
                        request, "admin/billing/upload_invoice.html", context
                    )
                except Exception as e:
                    logger.error(f"OCR processing error: {e}")
                    messages.error(request, f"Failed to process invoice: {str(e)}")
                    return render(
                        request, "admin/billing/upload_invoice.html", context
                    )

                # Create Invoice
                file.seek(0)  # Reset file pointer
                invoice = Invoice.objects.create(
                    organization=organization,
                    number=normalized_data.get("number", ""),
                    issue_date=normalized_data.get("issue_date"),
                    due_date=normalized_data.get("due_date"),
                    supplier_name=normalized_data.get("supplier", {}).get("name", ""),
                    supplier_tax_id=normalized_data.get("supplier", {}).get("tax_id"),
                    supplier_address=normalized_data.get("supplier", {}).get(
                        "address"
                    ),
                    buyer_name=normalized_data.get("buyer", {}).get("name", ""),
                    buyer_tax_id=normalized_data.get("buyer", {}).get("tax_id"),
                    buyer_address=normalized_data.get("buyer", {}).get("address"),
                    currency=normalized_data.get("currency", "USD"),
                    subtotal_amount=Decimal(
                        normalized_data.get("totals", {}).get("subtotal", "0")
                    ),
                    vat_amount=Decimal(
                        normalized_data.get("totals", {}).get("vat", "0")
                    ),
                    total_amount=Decimal(
                        normalized_data.get("totals", {}).get("total", "0")
                    ),
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

                messages.success(
                    request,
                    f"Successfully processed invoice {invoice.number} (ID: {invoice.id})",
                )

                # Add result to context
                context["result"] = {
                    "invoice_id": invoice.id,
                    "number": invoice.number,
                    "issue_date": invoice.issue_date,
                    "supplier": {
                        "name": invoice.supplier_name,
                    },
                    "buyer": {
                        "name": invoice.buyer_name,
                    },
                    "currency": invoice.currency,
                    "totals": {
                        "total": invoice.total_amount,
                    },
                    "provider_metadata": normalized_data.get("provider_metadata", {}),
                }

            except Exception as e:
                logger.error(f"Unexpected error in upload view: {e}")
                messages.error(request, f"An unexpected error occurred: {str(e)}")

        return render(request, "admin/billing/upload_invoice.html", context)

    def total_amount_display(self, obj):
        """Display total amount with formatting."""
        return format_html(
            '<span style="font-weight: bold; color: #2e7d32;">{}</span>',
            f"{obj.total_amount:.2f}",
        )

    total_amount_display.short_description = "Total Amount"
    total_amount_display.admin_order_field = "total_amount"

    def provider_badge(self, obj):
        """Display provider as colored badge."""
        colors = {
            "olmocr": "#1976d2",
            "marker_deepseek_r1": "#7b1fa2",
        }
        color = colors.get(obj.provider, "#757575")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_provider_display(),
        )

    provider_badge.short_description = "OCR Provider"
    provider_badge.admin_order_field = "provider"

    @admin.action(description="Export selected invoices as CSV")
    def export_as_csv(self, request, queryset):
        """Export selected invoices to CSV."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="invoices.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Invoice Number",
                "Organization",
                "Issue Date",
                "Due Date",
                "Supplier",
                "Buyer",
                "Currency",
                "Subtotal",
                "VAT",
                "Total",
                "Provider",
                "Created At",
            ]
        )

        for invoice in queryset:
            writer.writerow(
                [
                    invoice.number,
                    invoice.organization.name,
                    invoice.issue_date,
                    invoice.due_date or "",
                    invoice.supplier_name,
                    invoice.buyer_name,
                    invoice.currency,
                    invoice.subtotal_amount,
                    invoice.vat_amount,
                    invoice.total_amount,
                    invoice.get_provider_display(),
                    invoice.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        self.message_user(
            request, f"Exported {queryset.count()} invoice(s) to CSV successfully."
        )
        return response


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(ModelAdmin):
    """Admin for InvoiceLineItem model."""

    list_display = [
        "invoice",
        "description_short",
        "quantity",
        "unit",
        "unit_price",
        "tax_rate",
        "total",
    ]
    list_filter = ["invoice__organization", "invoice__provider"]
    search_fields = ["description", "invoice__number"]
    ordering = ["-id"]

    def description_short(self, obj):
        """Display truncated description."""
        max_length = 60
        if len(obj.description) > max_length:
            return f"{obj.description[:max_length]}..."
        return obj.description

    description_short.short_description = "Description"
