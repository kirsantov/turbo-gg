"""Local Ollama OCR provider implementation."""

import base64
import json
import logging
import time
from typing import IO

import httpx
from django.conf import settings

from .ocr_base import NormalizedInvoice

logger = logging.getLogger(__name__)


class OllamaLocalProvider:
    """OCR provider using local Ollama with vision models."""

    def __init__(self):
        self.ollama_url = getattr(settings, "OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = getattr(settings, "OLLAMA_MODEL", "llama3.2-vision")
        self.timeout = 60.0  # Vision models need more time

        if not self._check_ollama_available():
            logger.warning(
                f"Ollama not available at {self.ollama_url}, using mock mode"
            )
            self.ollama_url = None

    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "").split(":")[0] for m in models]
                    base_model = self.ollama_model.split(":")[0]
                    if base_model in model_names:
                        return True
                    logger.warning(
                        f"Model {self.ollama_model} not found. Available: {model_names}"
                    )
                    logger.info(f"Run: ollama pull {self.ollama_model}")
        except Exception as e:
            logger.debug(f"Ollama check failed: {e}")
        return False

    def parse_invoice(self, file: IO[bytes]) -> NormalizedInvoice:
        """Parse invoice using local Ollama vision model.

        Args:
            file: Invoice file (PDF or image)

        Returns:
            Normalized invoice structure

        Raises:
            ValueError: If OCR fails
            TimeoutError: If request times out
        """
        start_time = time.time()

        # If Ollama not available, return mock data
        if not self.ollama_url:
            return self._mock_response(start_time)

        try:
            # Read file content and encode to base64
            file.seek(0)
            file_content = file.read()
            file.seek(0)
            file_b64 = base64.b64encode(file_content).decode("utf-8")

            # Prepare prompt for vision model
            prompt = """Extract invoice data from this image and return ONLY a valid JSON object with this exact structure (no markdown, no extra text):

{
  "invoice_number": "string",
  "issue_date": "YYYY-MM-DD",
  "due_date": "YYYY-MM-DD or null",
  "currency": "USD",
  "subtotal": "0.00",
  "tax_amount": "0.00",
  "total": "0.00",
  "supplier_name": "string",
  "supplier_tax_id": "string or null",
  "supplier_address": "string or null",
  "buyer_name": "string",
  "buyer_tax_id": "string or null",
  "buyer_address": "string or null",
  "line_items": [
    {
      "description": "string",
      "quantity": "1.00",
      "unit": "pcs",
      "unit_price": "0.00",
      "tax_rate": "0.00",
      "total": "0.00"
    }
  ]
}

Return ONLY the JSON, nothing else."""

            # Call Ollama API with vision
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "images": [file_b64],
                        "stream": False,
                        "format": "json",  # Request JSON response
                    },
                )

            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} {response.text}")
                raise ValueError(f"Ollama API returned {response.status_code}")

            result = response.json()
            response_text = result.get("response", "")

            # Parse JSON response
            try:
                # Try to extract JSON if wrapped in markdown
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                data = json.loads(response_text.strip())
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Ollama: {e}")
                logger.error(f"Response was: {response_text[:500]}")
                raise ValueError(f"Invalid JSON response from Ollama: {e}")

            latency_ms = int((time.time() - start_time) * 1000)
            return self._normalize_response(data, latency_ms)

        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise TimeoutError("Ollama OCR request timed out")
        except httpx.RequestError as e:
            logger.error(f"Ollama request failed: {e}")
            raise ValueError(f"Ollama OCR request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama OCR: {e}")
            raise ValueError(f"Ollama OCR failed: {e}")

    def _normalize_response(
        self, data: dict, latency_ms: int
    ) -> NormalizedInvoice:
        """Normalize Ollama response to standard format."""
        return {
            "number": data.get("invoice_number", "N/A"),
            "issue_date": data.get("issue_date", "2024-01-01"),
            "due_date": data.get("due_date"),
            "supplier": {
                "name": data.get("supplier_name", "Unknown Supplier"),
                "tax_id": data.get("supplier_tax_id"),
                "address": data.get("supplier_address"),
            },
            "buyer": {
                "name": data.get("buyer_name", "Unknown Buyer"),
                "tax_id": data.get("buyer_tax_id"),
                "address": data.get("buyer_address"),
            },
            "currency": data.get("currency", "USD"),
            "totals": {
                "subtotal": str(data.get("subtotal", "0.00")),
                "vat": str(data.get("tax_amount", "0.00")),
                "total": str(data.get("total", "0.00")),
            },
            "line_items": [
                {
                    "description": item.get("description", "N/A"),
                    "quantity": str(item.get("quantity", "1.00")),
                    "unit": item.get("unit", "pcs"),
                    "unit_price": str(item.get("unit_price", "0.00")),
                    "tax_rate": str(item.get("tax_rate", "0.00"))
                    if item.get("tax_rate")
                    else None,
                    "total": str(item.get("total", "0.00")),
                }
                for item in data.get("line_items", [])
            ],
            "raw_text": None,
            "provider_metadata": {
                "name": "ollama_local",
                "confidence": 0.85,  # Ollama doesn't provide confidence
                "latency_ms": latency_ms,
            },
        }

    def _mock_response(self, start_time: float) -> NormalizedInvoice:
        """Return mock data when Ollama is not available."""
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "number": "INV-2025-LOCAL-001",
            "issue_date": "2025-11-11",
            "due_date": "2025-12-11",
            "supplier": {
                "name": "Local Supplier (Ollama Mock)",
                "tax_id": "US-00-0000000",
                "address": "123 Local St, GPU City, GC 12345",
            },
            "buyer": {
                "name": "Local Buyer (Ollama Mock)",
                "tax_id": "US-11-1111111",
                "address": "456 Local Ave, ML Town, ML 67890",
            },
            "currency": "USD",
            "totals": {
                "subtotal": "1000.00",
                "vat": "100.00",
                "total": "1100.00",
            },
            "line_items": [
                {
                    "description": "GPU Computing Hours (Mock)",
                    "quantity": "10.000",
                    "unit": "hours",
                    "unit_price": "50.00",
                    "tax_rate": "10.00",
                    "total": "500.00",
                },
                {
                    "description": "ML Model Training (Mock)",
                    "quantity": "5.000",
                    "unit": "jobs",
                    "unit_price": "100.00",
                    "tax_rate": "10.00",
                    "total": "500.00",
                },
            ],
            "raw_text": "Mock OCR text extraction (local Ollama provider)",
            "provider_metadata": {
                "name": "ollama_local",
                "confidence": 0.0,  # Mock data
                "latency_ms": latency_ms,
            },
        }
