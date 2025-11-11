"""URL configuration for billing app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InvoiceViewSet, OrganizationViewSet, ocr_invoice_upload

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"invoices", InvoiceViewSet, basename="invoice")

app_name = "billing"

urlpatterns = [
    # OCR endpoint - must be exact path /ocr/invoice
    path("ocr/invoice", ocr_invoice_upload, name="ocr-invoice-upload"),
    # API endpoints
    path("api/", include(router.urls)),
]
