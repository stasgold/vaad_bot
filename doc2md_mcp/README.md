# doc2md MCP

MCP server that converts documents to Markdown using `markdown[all]` plus common extraction libraries.

## Tools
- `doc2md`: Convert a local file path into Markdown and metadata.

## Language Support
- **Hebrew + English OCR**: Automatically uses Hebrew and English language detection for images
- Supports Israeli bank statements, payment screenshots, and mixed Hebrew/English documents

## Installation

### Prerequisites
Install Tesseract OCR with Hebrew language support:

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-heb
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

## Run
Install dependencies and run the server:
- `python server.py`

## Notes
- For images, OCR requires Tesseract to be installed on the system with Hebrew language data.
- Hebrew OCR works best with clear, high-resolution images.
- Unsupported file types will attempt a best‑effort text decode.
