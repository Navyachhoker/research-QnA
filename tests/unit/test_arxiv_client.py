from unittest.mock import MagicMock, patch

import pytest

from app.rag.arxiv_client import ArxivError, _validate_arxiv_id, download_arxiv_pdf, search_arxiv

SAMPLE_ATOM_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v5</id>
    <title>Attention Is All You Need</title>
    <summary>We propose a new network architecture.</summary>
    <published>2017-06-12T00:00:00Z</published>
    <author><name>Ashish Vaswani</name></author>
  </entry>
</feed>"""


def test_validate_arxiv_id_accepts_valid_id():
    assert _validate_arxiv_id("2103.12345") == "2103.12345"
    assert _validate_arxiv_id("1706.03762v5") == "1706.03762v5"


@pytest.mark.parametrize("bad_id", ["../../etc/passwd", "'; DROP TABLE papers;--", "not-an-id", ""])
def test_validate_arxiv_id_rejects_malicious_or_malformed_input(bad_id):
    with pytest.raises(ArxivError):
        _validate_arxiv_id(bad_id)


def test_search_arxiv_parses_atom_feed():
    mock_response = MagicMock()
    mock_response.text = SAMPLE_ATOM_FEED
    mock_response.raise_for_status = MagicMock()

    with patch("app.rag.arxiv_client.httpx.get", return_value=mock_response):
        results = search_arxiv("attention is all you need")

    assert len(results) == 1
    assert results[0]["arxiv_id"] == "1706.03762v5"
    assert results[0]["title"] == "Attention Is All You Need"
    assert results[0]["authors"] == ["Ashish Vaswani"]


def test_download_arxiv_pdf_rejects_invalid_id(tmp_path):
    with pytest.raises(ArxivError):
        download_arxiv_pdf("../../etc/passwd", tmp_path / "out.pdf")
