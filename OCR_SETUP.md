# OCR Providers Setup Guide

This project supports two OCR providers for invoice processing. By default, the system runs in **mock mode** for testing without API keys.

## Mock Mode (Default)

If OCR providers are not configured, the system returns realistic mock data:
- Mock invoices with sample company names
- Random amounts and dates
- Sample line items

This is useful for:
- Testing the UI and workflow
- Development without external dependencies
- Demos

## Real OCR Providers

### Option 1: OlmOCR (Recommended for simplicity)

**What is it?** A self-hosted OCR API using Ollama models (llama-vision or similar).

**Setup:**

1. **Deploy OlmOCR:**
   ```bash
   git clone https://github.com/yigitkonur/ollama-ocr-api
   cd ollama-ocr-api
   # Follow their installation instructions
   # Usually: docker-compose up -d
   ```

2. **Configure in `.env.backend`:**
   ```bash
   OLMOCR_API_URL=http://your-olmocr-server:8080
   OLMOCR_API_KEY=your-api-key-if-required
   ```

3. **Restart backend:**
   ```bash
   # Kill existing server and restart
   uv run python manage.py runserver
   ```

**Pros:**
- Self-hosted (free, unlimited)
- Good accuracy for invoices
- Single-step processing

**Cons:**
- Requires GPU for good performance
- Need to deploy and maintain

---

### Option 2: Marker + DeepSeek R1

**What is it?** Two-step pipeline:
1. **Marker**: Converts PDF to structured markdown
2. **DeepSeek R1**: LLM extracts invoice data from markdown

**Setup:**

1. **Deploy Marker API:**
   ```bash
   git clone https://github.com/VikParuchuri/marker
   cd marker
   # Follow their API server setup
   ```

2. **Get DeepSeek API Key:**
   - Sign up at https://platform.deepseek.com/
   - Get your API key from dashboard
   - DeepSeek R1 is very cheap (~$0.14 per 1M input tokens)

3. **Configure in `.env.backend`:**
   ```bash
   MARKER_API_URL=http://your-marker-server:8000
   MARKER_API_KEY=your-marker-key-if-required
   DEEPSEEK_API_KEY=your-deepseek-key
   DEEPSEEK_MODEL=deepseek-r1  # or deepseek-chat
   ```

4. **Restart backend**

**Pros:**
- Marker is excellent at PDF structure extraction
- DeepSeek R1 is very cheap and accurate
- Good for complex invoices

**Cons:**
- Two services to manage
- Slightly slower (two API calls)
- Costs money for DeepSeek (but minimal)

---

## Quick Start: Using Mock Mode

If you just want to test the system without setting up OCR:

1. Leave `.env.backend` OCR settings empty (they already are)
2. Upload any PDF/image file
3. System will return realistic mock invoice data
4. All features work normally (save, view, filter, etc.)

---

## Alternative: Use Cloud OCR Services

You can also modify the providers to use cloud services:

### Google Cloud Vision API
- High accuracy
- Pay per use
- Need to modify `ocr_olmocr.py` to call their API

### AWS Textract
- Good for invoices specifically
- Has invoice-specific extraction features
- Need to modify provider code

### Azure Form Recognizer
- Invoice prebuilt model
- Very accurate for standard invoices
- Need to modify provider code

---

## Testing Your OCR Setup

1. **Check logs when uploading:**
   ```bash
   # Backend logs will show:
   # "OLMOCR_API_URL not configured, using mock mode" (if not set up)
   # OR actual API calls and responses
   ```

2. **Upload a real invoice PDF**

3. **Check the result:**
   - Mock mode: Returns "Mock Service", "Mock Buyer Inc"
   - Real OCR: Returns actual extracted data from your invoice

4. **Debug mode:**
   - Set `DEBUG=1` in `.env.backend` (already set)
   - Check backend console for detailed logs

---

## Current Status

```bash
# Check current OCR configuration:
grep "OLMOCR\|MARKER\|DEEPSEEK" /home/user/turbo-gg/.env.backend
```

**Currently configured:** Mock mode (all OCR settings empty)

---

## Need Help?

- **OlmOCR Issues:** https://github.com/yigitkonur/ollama-ocr-api/issues
- **Marker Issues:** https://github.com/VikParuchuri/marker/issues
- **DeepSeek API:** https://api-docs.deepseek.com/

---

## Performance Comparison

| Provider | Speed | Accuracy | Cost | Setup Difficulty |
|----------|-------|----------|------|------------------|
| Mock | Instant | N/A | Free | None |
| OlmOCR | 2-5s | Good | Free* | Medium (self-host) |
| Marker+DeepSeek | 3-8s | Very Good | ~$0.01/invoice | Medium (two services) |
| Cloud APIs | 1-3s | Excellent | $0.10-1.00/invoice | Easy |

*Requires GPU hardware
