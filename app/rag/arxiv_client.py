"""Thin client for the public arXiv API (http://export.arxiv.org/api)."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

_ARXIV_API_URL = "http://export.arxiv.org/api/query"
_ATOM_NS = "{http://www.w3.org/2005/Atom}"
_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")


class ArxivError(RuntimeError):
    pass


def _validate_arxiv_id(arxiv_id: str) -> str:
    """Defense in depth: this id can end up in a URL and a filesystem path
    (see arxiv_service.import_paper_from_arxiv), so reject anything that
    isn't a plausible arXiv id before it's used for either."""
    arxiv_id = arxiv_id.strip()
    if not _ID_RE.match(arxiv_id):
        raise ArxivError(f"'{arxiv_id}' doesn't look like a valid arXiv id (expected e.g. '2103.12345').")
    return arxiv_id


def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """Search arXiv by free-text query or arXiv id. Returns
    [{"arxiv_id", "title", "authors", "summary", "published"}]."""
    max_results = max(1, min(max_results, 25))

    params: dict[str, str | int]
    if _ID_RE.match(query.strip()):
        params = {"id_list": query.strip(), "max_results": 1}
    else:
        params = {"search_query": f"all:{query}", "max_results": max_results}

    try:
        response = httpx.get(_ARXIV_API_URL, params=params, timeout=15.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ArxivError(f"arXiv search failed: {exc}") from exc

    root = ET.fromstring(response.text)
    results = []
    for entry in root.findall(f"{_ATOM_NS}entry"):
        raw_id = entry.findtext(f"{_ATOM_NS}id", default="")
        arxiv_id = raw_id.rsplit("/abs/", 1)[-1] if "/abs/" in raw_id else raw_id
        results.append(
            {
                "arxiv_id": arxiv_id,
                "title": (entry.findtext(f"{_ATOM_NS}title") or "").strip().replace("\n", " "),
                "authors": [a.findtext(f"{_ATOM_NS}name") for a in entry.findall(f"{_ATOM_NS}author")],
                "summary": (entry.findtext(f"{_ATOM_NS}summary") or "").strip(),
                "published": entry.findtext(f"{_ATOM_NS}published"),
            }
        )
    return results


def download_arxiv_pdf(arxiv_id: str, dest_path: str | Path) -> Path:
    """Download the PDF for a given arXiv id to dest_path."""
    arxiv_id = _validate_arxiv_id(arxiv_id)
    dest_path = Path(dest_path)
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    try:
        with httpx.stream("GET", url, timeout=30.0, follow_redirects=True) as response:
            response.raise_for_status()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
    except httpx.HTTPError as exc:
        raise ArxivError(f"Failed to download arXiv PDF '{arxiv_id}': {exc}") from exc

    return dest_path
