"""Marker + DeepSeek R1 provider implementation."""

import logging
import time
from io import BytesIO
from typing import IO

import httpx
from django.conf import settings

from .ocr_base import NormalizedInvoice

logger = logging.getLogger(__name__)


class MarkerDeepseekProvider:
    """OCR provider using Marker PDF converter + DeepSeek R1 LLM."""

    def __init__(self):
        self.marker_api_url = getattr(settings, "MARKER_API_URL", None)
        self.marker_api_key = getattr(settings, "MARKER_API_KEY", None)
        self.deepseek_model = getattr(settings, "DEEPSEEK_MODEL", "r1")
        self.timeout = 30.0

        if not self.marker_api_url:
            logger.warning("MARKER_API_URL not configured, using mock mode")

    def parse_invoice(self, file: IO[bytes]) -> NormalizedInvoice:
        """Parse invoice using Marker + DeepSeek.

        Two-step process:
        1. Convert PDF to structured text with Marker
        2. Extract invoice data with DeepSeek R1

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
        if not self.marker_api_url:
            return self._mock_response(start_time)

        try:
            # Step 1: Convert with Marker
            markdown_text = self._convert_with_marker(file)

            # Step 2: Extract structured data with DeepSeek
            invoice_data = self._extract_with_deepseek(markdown_text)

            latency_ms = int((time.time() - start_time) * 1000)

            # Normalize to our schema
            return self._normalize_response(invoice_data, markdown_text, latency_ms)

        except httpx.TimeoutException as e:
            logger.error(f"Marker/DeepSeek timeout: {e}")
            raise TimeoutError("Marker/DeepSeek request timed out") from e
        except Exception as e:
            logger.error(f"Marker/DeepSeek error: {e}")
            raise ValueError(
                f"Failed to process invoice with Marker/DeepSeek: {e}"
            ) from e

    def _convert_with_marker(self, file: IO[bytes]) -> str:
        """Convert PDF to markdown with Marker.

        Args:
            file: PDF file

        Returns:
            Markdown text
        """
        file.seek(0)
        file_content = file.read()
        file.seek(0)

        headers = {}
        if self.marker_api_key:
            headers["Authorization"] = f"Bearer {self.marker_api_key}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.marker_api_url}/convert",
                files={"file": ("invoice.pdf", BytesIO(file_content))},
                headers=headers,
            )

        if response.status_code != 200:
            raise ValueError(
                f"Marker API error: {response.status_code} - {response.text}"
            )

        data = response.json()
        return data.get("markdown", "")

    def _extract_with_deepseek(self, text: str) -> dict:
        """Extract invoice data using DeepSeek R1.

        Args:
            text: Markdown text from Marker

        Returns:
            Extracted invoice data
        """
        # In real implementation, call DeepSeek API with structured prompt
        # For now, return mock structured data

        prompt = f"""Extract invoice information from the following text and return as JSON:

Text:
{text[:2000]}

Return JSON with fields: invoice_number, issue_date, due_date, supplier (name, tax_id, address),
buyer (name, tax_id, address), currency, subtotal, vat, total, line_items (description, quantity,
unit, unit_price, tax_rate, total)
"""

        # TODO: Implement actual DeepSeek API call
        # response = deepseek_client.chat(model=self.deepseek_model, messages=[...])

        # Mock response
        return {
            "invoice_number": "INV-MARKER-001",
            "issue_date": "2025-11-11",
            "due_date": "2025-12-11",
            "supplier": {
                "name": "Marker Supplier Co",
                "tax_id": "US-22-2222222",
                "address": "789 Marker Rd, AI City, AC 11111",
            },
            "buyer": {
                "name": "DeepSeek Buyer Ltd",
                "tax_id": "US-33-3333333",
                "address": "321 DeepSeek Blvd, ML Town, ML 99999",
            },
            "currency": "USD",
            "subtotal": 1500.00,
            "vat": 120.00,
            "total": 1620.00,
            "line_items": [
                {
                    "description": "AI Processing Service",
                    "quantity": 2.0,
                    "unit": "hours",
                    "unit_price": 750.00,
                    "tax_rate": 8.00,
                    "total": 1500.00,
                }
            ],
        }

    def _normalize_response(
        self, data: dict, raw_text: str, latency_ms: int
    ) -> NormalizedInvoice:
        """Convert Marker/DeepSeek response to normalized format.

        Args:
            data: Extracted invoice data
            raw_text: Original markdown text
            latency_ms: Request latency

        Returns:
            Normalized invoice
        """
        return {
            "number": data.get("invoice_number", ""),
            "issue_date": data.get("issue_date", ""),
            "due_date": data.get("due_date"),
            "supplier": {
                "name": data.get("supplier", {}).get("name", ""),
                "tax_id": data.get("supplier", {}).get("tax_id"),
                "address": data.get("supplier", {}).get("address"),
            },
            "buyer": {
                "name": data.get("buyer", {}).get("name", ""),
                "tax_id": data.get("buyer", {}).get("tax_id"),
                "address": data.get("buyer", {}).get("address"),
            },
            "currency": data.get("currency", "USD"),
            "totals": {
                "subtotal": str(data.get("subtotal", "0.00")),
                "vat": str(data.get("vat", "0.00")),
                "total": str(data.get("total", "0.00")),
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
                for item in data.get("line_items", [])
            ],
            "raw_text": raw_text,
            "provider_metadata": {
                "name": "marker_deepseek_r1",
                "confidence": 0.90,  # Could be derived from DeepSeek response
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
            "number": "INV-2025-MOCK-002",
            "issue_date": "2025-11-11",
            "due_date": "2025-12-11",
            "supplier": {
                "name": "Marker Mock Supplier",
                "tax_id": "US-44-4444444",
                "address": "999 Mock Lane, Test City, TC 55555",
            },
            "buyer": {
                "name": "DeepSeek Mock Buyer",
                "tax_id": "US-55-5555555",
                "address": "888 Mock Blvd, Test Town, TT 66666",
            },
            "currency": "USD",
            "totals": {
                "subtotal": "2000.00",
                "vat": "160.00",
                "total": "2160.00",
            },
            "line_items": [
                {
                    "description": "Mock AI Analysis",
                    "quantity": "10.000",
                    "unit": "units",
                    "unit_price": "200.00",
                    "tax_rate": "8.00",
                    "total": "2000.00",
                }
            ],
            "raw_text": "Mock OCR text extraction (Marker + DeepSeek R1 provider)",
            "provider_metadata": {
                "name": "marker_deepseek_r1",
                "confidence": 0.92,
                "latency_ms": latency_ms,
            },
        }
