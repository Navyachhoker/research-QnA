import pytest

from app.utils.pdf_utils import PDFExtractionError, extract_text_by_page


def test_extract_text_by_page_missing_file(tmp_path):
    with pytest.raises(PDFExtractionError):
        extract_text_by_page(tmp_path / "does_not_exist.pdf")


def test_extract_text_by_page_corrupt_file(tmp_path):
    bad_pdf = tmp_path / "corrupt.pdf"
    bad_pdf.write_bytes(b"this is not a real pdf file at all")
    with pytest.raises(PDFExtractionError):
        extract_text_by_page(bad_pdf)


def test_extract_text_by_page_extracts_real_content(tmp_path, sample_pdf_bytes):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)

    pages = extract_text_by_page(pdf_path)

    assert len(pages) == 2
    assert "transformers" in pages[0]["text"]
    assert pages[0]["page_number"] == 1
    assert "experimental results" in pages[1]["text"]
    assert pages[1]["page_number"] == 2


def test_extract_text_by_page_no_text_layer(tmp_path):
    import fitz

    doc = fitz.open()
    doc.new_page()  # blank page, no text
    blank_path = tmp_path / "blank.pdf"
    doc.save(blank_path)
    doc.close()

    with pytest.raises(PDFExtractionError):
        extract_text_by_page(blank_path)
