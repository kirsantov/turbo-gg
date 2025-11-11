"""Admin configuration for billing app with django-unfold."""

import csv
from decimal import Decimal

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import Invoice, InvoiceLineItem, Organization


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
