"""Unit tests for document format detection and text extraction."""

import unittest

from masar.application.services.document_extractor import (
    detect_file_type,
    extract_text_from_bytes,
)
from masar.domain.exceptions.document import (
    DocumentExtractionError,
    EmptyDocumentError,
    UnsupportedFileTypeError,
)

SAMPLE_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    b"4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 72 712 Td (Hello Masar Learning) Tj ET\nendstream\nendobj\n"
    b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000227 00000 n \n0000000321 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n393\n%%EOF"
)


class TestDocumentExtractor(unittest.TestCase):
    """Test suite for Document file type detection and text extraction."""

    def test_detect_file_type_by_extension(self) -> None:
        self.assertEqual(detect_file_type("resume.pdf"), "pdf")
        self.assertEqual(detect_file_type("NOTES.TXT"), "text")
        self.assertEqual(detect_file_type("README.md"), "markdown")
        self.assertEqual(detect_file_type("spec.markdown"), "markdown")

    def test_detect_file_type_unsupported(self) -> None:
        with self.assertRaises(UnsupportedFileTypeError):
            detect_file_type("binary.exe")
        with self.assertRaises(UnsupportedFileTypeError):
            detect_file_type("data.docx")

    def test_extract_text_from_plain_text(self) -> None:
        content = "Python Architecture and Design Patterns\n1. Separation of concerns\n2. Layering"
        file_type, text = extract_text_from_bytes(content.encode("utf-8"), "notes.txt")
        self.assertEqual(file_type, "text")
        self.assertEqual(text, content)

    def test_extract_text_from_markdown(self) -> None:
        content = "# Distributed Systems Roadmap\n\n- Raft consensus\n- Paxos\n- Vector Clocks"
        file_type, text = extract_text_from_bytes(content.encode("utf-8"), "roadmap.md")
        self.assertEqual(file_type, "markdown")
        self.assertEqual(text, content)

    def test_extract_text_from_pdf(self) -> None:
        file_type, text = extract_text_from_bytes(SAMPLE_PDF, "sample.pdf")
        self.assertEqual(file_type, "pdf")
        self.assertIn("Hello Masar Learning", text)

    def test_extract_empty_file_raises_error(self) -> None:
        with self.assertRaises(EmptyDocumentError):
            extract_text_from_bytes(b"", "empty.txt")
        with self.assertRaises(EmptyDocumentError):
            extract_text_from_bytes(b"   \n  \t", "whitespace.txt")

    def test_extract_corrupted_pdf_raises_extraction_error(self) -> None:
        corrupt_pdf = b"%PDF-invalid-bytes-not-a-real-pdf"
        with self.assertRaises(DocumentExtractionError):
            extract_text_from_bytes(corrupt_pdf, "broken.pdf")
