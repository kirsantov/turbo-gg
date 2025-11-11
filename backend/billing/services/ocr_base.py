"""Base OCR provider protocol and factory."""

import logging
from typing import IO, Protocol, TypedDict

logger = logging.getLogger(__name__)


class SupplierBuyer(TypedDict, total=False):
    """Supplier or Buyer information."""

    name: str
    tax_id: str | None
    address: str | None


class Totals(TypedDict):
    """Invoice totals."""

    subtotal: str
    vat: str
    total: str


class LineItem(TypedDict):
    """Invoice line item."""

    description: str
    quantity: str
    unit: str | None
    unit_price: str
    tax_rate: str | None
    total: str


class ProviderMetadata(TypedDict, total=False):
    """OCR provider metadata."""

    name: str
    confidence: float
    latency_ms: int


class NormalizedInvoice(TypedDict, total=False):
    """Normalized invoice structure returned by all OCR providers."""

    number: str
    issue_date: str
    due_date: str | None
    supplier: SupplierBuyer
    buyer: SupplierBuyer
    currency: str
    totals: Totals
    line_items: list[LineItem]
    raw_text: str | None
    provider_metadata: ProviderMetadata


class OCRProvider(Protocol):
    """Protocol for OCR providers."""

    def parse_invoice(self, file: IO[bytes]) -> NormalizedInvoice:
        """Parse invoice file and return normalized structure.

        Args:
            file: File-like object (PDF, image, etc.)

        Returns:
            NormalizedInvoice dict with standardized structure

        Raises:
            ValueError: If parsing fails or data is invalid
            TimeoutError: If OCR service times out
        """
        ...


def get_ocr_provider(provider_name: str) -> OCRProvider:
    """Factory to get OCR provider instance.

    Args:
        provider_name: Provider identifier ('ollama_local', 'olmocr', or 'marker_deepseek_r1')

    Returns:
        OCRProvider instance

    Raises:
        ValueError: If provider_name is unknown
    """
    from .ocr_marker_deepseek import MarkerDeepseekProvider
    from .ocr_ollama_local import OllamaLocalProvider
    from .ocr_olmocr import OlmOCRProvider

    providers = {
        "ollama_local": OllamaLocalProvider,
        "olmocr": OlmOCRProvider,
        "marker_deepseek_r1": MarkerDeepseekProvider,
    }

    provider_class = providers.get(provider_name)
    if not provider_class:
        raise ValueError(
            f"Unknown OCR provider: {provider_name}. "
            f"Available: {', '.join(providers.keys())}"
        )

    return provider_class()
