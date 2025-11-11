"""OlmOCR provider implementation."""

import logging
import time
from io import BytesIO
from typing import IO

import httpx
from django.conf import settings

from .ocr_base import NormalizedInvoice

logger = logging.getLogger(__name__)


class OlmOCRProvider:
    """OCR provider using OlmOCR API."""

    def __init__(self):
        self.api_url = getattr(settings, "OLMOCR_API_URL", None)
        self.api_key = getattr(settings, "OLMOCR_API_KEY", None)
        self.timeout = 30.0

        if not self.api_url:
            logger.warning("OLMOCR_API_URL not configured, using mock mode")

    def parse_invoice(self, file: IO[bytes]) -> NormalizedInvoice:
        """Parse invoice using OlmOCR.

        Args:
            file: Invoice file (PDF or image)

        Returns:
            Normalized invoice structure

        Raises:
            ValueError: If OCR fails
            TimeoutError: If request times out
        """
        start_time = time.time()

        # If no API configured, return mock data
        if not self.api_url:
            return self._mock_response(start_time)

        try:
            # Read file content
            file.seek(0)
            file_content = file.read()
            file.seek(0)

            # Prepare request
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Call OlmOCR API
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.api_url}/ocr/invoice",
                    files={"file": ("invoice.pdf", BytesIO(file_content))},
                    headers=headers,
                )

            if response.status_code != 200:
                raise ValueError(
                    f"OlmOCR API error: {response.status_code} - {response.text}"
                )

            # Parse response
            data = response.json()
            latency_ms = int((time.time() - start_time) * 1000)

            # Normalize to our schema
            return self._normalize_response(data, latency_ms)

        except httpx.TimeoutException as e:
            logger.error(f"OlmOCR timeout: {e}")
            raise TimeoutError("OlmOCR request timed out") from e
        except Exception as e:
            logger.error(f"OlmOCR error: {e}")
            raise ValueError(f"Failed to process invoice with OlmOCR: {e}") from e

    def _normalize_response(self, data: dict, latency_ms: int) -> NormalizedInvoice:
        """Convert OlmOCR response to normalized format.

        Args:
            data: Raw OlmOCR response
            latency_ms: Request latency

        Returns:
            Normalized invoice
        """
        # Extract fields (adapt to actual OlmOCR API response structure)
        invoice_data = data.get("invoice", {})

        return {
            "number": invoice_data.get("invoice_number", ""),
            "issue_date": invoice_data.get("issue_date", ""),
            "due_date": invoice_data.get("due_date"),
            "supplier": {
                "name": invoice_data.get("supplier", {}).get("name", ""),
                "tax_id": invoice_data.get("supplier", {}).get("tax_id"),
                "address": invoice_data.get("supplier", {}).get("address"),
            },
            "buyer": {
                "name": invoice_data.get("buyer", {}).get("name", ""),
                "tax_id": invoice_data.get("buyer", {}).get("tax_id"),
                "address": invoice_data.get("buyer", {}).get("address"),
            },
            "currency": invoice_data.get("currency", "USD"),
            "totals": {
                "subtotal": str(invoice_data.get("subtotal", "0.00")),
                "vat": str(invoice_data.get("vat", "0.00")),
                "total": str(invoice_data.get("total", "0.00")),
            },
            "line_items": [
                {
                    "description": item.get("description", ""),
                    "quantity": str(item.get("quantity", "1")),
                    "unit": item.get("unit"),
                    "unit_price": str(item.get("unit_price", "0.00")),
                    "tax_rate": str(item.get("tax_rate"))
                    if item.get("tax_rate")
                    else None,
                    "total": str(item.get("total", "0.00")),
                }
                for item in invoice_data.get("line_items", [])
            ],
            "raw_text": data.get("raw_text"),
            "provider_metadata": {
                "name": "olmocr",
                "confidence": data.get("confidence", 0.0),
                "latency_ms": latency_ms,
            },
        }

    def _mock_response(self, start_time: float) -> NormalizedInvoice:
        """Return mock response for testing without real API.

        Args:
            start_time: Request start timestamp

        Returns:
            Mock normalized invoice
        """
        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "number": "INV-2025-MOCK-001",
            "issue_date": "2025-11-11",
            "due_date": "2025-12-11",
            "supplier": {
                "name": "Mock Supplier LLC",
                "tax_id": "US-00-0000000",
                "address": "123 Mock St, Test City, TC 12345",
            },
            "buyer": {
                "name": "Mock Buyer Inc",
                "tax_id": "US-11-1111111",
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
                    "description": "Mock Service",
                    "quantity": "1.000",
                    "unit": "service",
                    "unit_price": "1000.00",
                    "tax_rate": "8.00",
                    "total": "1000.00",
                }
            ],
            "raw_text": "Mock OCR text extraction (olmOCR provider)",
            "provider_metadata": {
                "name": "olmocr",
                "confidence": 0.95,
                "latency_ms": latency_ms,
            },
        }
