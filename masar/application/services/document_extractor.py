"""Document text extraction engine supporting PDF, Plain Text, and Markdown."""

import io
from pathlib import Path
from typing import Tuple

from masar.domain.exceptions.document import (
    DocumentExtractionError,
    EmptyDocumentError,
    UnsupportedFileTypeError,
)


def detect_file_type(filename: str) -> str:
    """Determine normalized file type based on file extension."""
    suffix = Path(filename).suffix.lower()
    if suffix in (".pdf",):
        return "pdf"
    if suffix in (".txt", ".text"):
        return "text"
    if suffix in (".md", ".markdown"):
        return "markdown"
    raise UnsupportedFileTypeError(
        f"Unsupported file format '{suffix}'. Supported formats are: PDF (.pdf), Text (.txt), and Markdown (.md)."
    )


def extract_text_from_bytes(content_bytes: bytes, filename: str) -> Tuple[str, str]:
    """Extract text from raw document bytes based on file format.

    Returns:
        Tuple of (normalized_file_type, extracted_text)
    Raises:
        EmptyDocumentError: If the document contains no readable text.
        DocumentExtractionError: If file is corrupted or cannot be parsed.
    """
    file_type = detect_file_type(filename)

    if not content_bytes or len(content_bytes.strip()) == 0:
        raise EmptyDocumentError(f"Uploaded file '{filename}' is empty (0 bytes).")

    if file_type in ("text", "markdown"):
        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content_bytes.decode("latin-1")
            except Exception as exc:
                raise DocumentExtractionError(
                    f"Could not decode text file '{filename}': {exc}"
                ) from exc

        clean_text = text.strip()
        if not clean_text:
            raise EmptyDocumentError(
                f"Uploaded text document '{filename}' contains no readable content."
            )
        return file_type, clean_text

    if file_type == "pdf":
        try:
            import pypdf

            stream = io.BytesIO(content_bytes)
            reader = pypdf.PdfReader(stream)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as exc:
                    raise DocumentExtractionError(
                        f"Cannot read password-protected or encrypted PDF '{filename}'."
                    ) from exc

            pages_text: list[str] = []
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    page_str = page.extract_text() or ""
                    if page_str.strip():
                        pages_text.append(f"--- Page {page_num} ---\n{page_str.strip()}")
                except Exception:
                    continue

            extracted = "\n\n".join(pages_text).strip()
            if not extracted:
                # Scanned or image-only PDF
                return file_type, "[Note: This PDF appears to be scanned or contains only images without embedded text layer.]"

            return file_type, extracted
        except Exception as exc:
            if isinstance(exc, (DocumentExtractionError, EmptyDocumentError)):
                raise
            raise DocumentExtractionError(
                f"Failed to parse and extract text from PDF '{filename}': {exc}"
            ) from exc

    raise UnsupportedFileTypeError(f"Unsupported file format for '{filename}'.")
