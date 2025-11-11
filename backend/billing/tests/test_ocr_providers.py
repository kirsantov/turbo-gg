"""Tests for OCR providers."""

from io import BytesIO
from unittest.mock import Mock, patch

import pytest

from billing.services import MarkerDeepseekProvider, OlmOCRProvider, get_ocr_provider


class TestOCRProviderFactory:
    """Tests for OCR provider factory."""

    def test_get_olmocr_provider(self):
        """Test getting olmocr provider."""
        provider = get_ocr_provider("olmocr")
        assert isinstance(provider, OlmOCRProvider)

    def test_get_marker_deepseek_provider(self):
        """Test getting marker_deepseek_r1 provider."""
        provider = get_ocr_provider("marker_deepseek_r1")
        assert isinstance(provider, MarkerDeepseekProvider)

    def test_get_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown OCR provider"):
            get_ocr_provider("invalid_provider")


class TestOlmOCRProvider:
    """Tests for OlmOCR provider."""

    def test_parse_invoice_mock_mode(self):
        """Test parsing invoice in mock mode (no API configured)."""
        provider = OlmOCRProvider()
        # Provider should use mock mode when API URL not configured
        assert provider.api_url == ""

        file = BytesIO(b"fake pdf content")
        result = provider.parse_invoice(file)

        assert result["number"] == "INV-2025-MOCK-001"
        assert result["currency"] == "USD"
        assert result["provider_metadata"]["name"] == "olmocr"
        assert "confidence" in result["provider_metadata"]


class TestMarkerDeepseekProvider:
    """Tests for Marker + DeepSeek provider."""

    def test_parse_invoice_mock_mode(self):
        """Test parsing invoice in mock mode (no API configured)."""
        provider = MarkerDeepseekProvider()
        # Provider should use mock mode when API URL not configured
        assert provider.marker_api_url == ""

        file = BytesIO(b"fake pdf content")
        result = provider.parse_invoice(file)

        assert result["number"] == "INV-2025-MOCK-002"
        assert result["currency"] == "USD"
        assert result["provider_metadata"]["name"] == "marker_deepseek_r1"
        assert "confidence" in result["provider_metadata"]
