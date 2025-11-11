"""Filters for billing app."""

import django_filters

from .models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    """Filter for Invoice model."""

    organization = django_filters.NumberFilter(field_name="organization__id")
    number = django_filters.CharFilter(field_name="number", lookup_expr="icontains")
    issue_date_from = django_filters.DateFilter(
        field_name="issue_date", lookup_expr="gte"
    )
    issue_date_to = django_filters.DateFilter(field_name="issue_date", lookup_expr="lte")
    provider = django_filters.ChoiceFilter(
        choices=Invoice.PROVIDER_CHOICES,
    )

    class Meta:
        model = Invoice
        fields = ["organization", "number", "provider", "issue_date_from", "issue_date_to"]
