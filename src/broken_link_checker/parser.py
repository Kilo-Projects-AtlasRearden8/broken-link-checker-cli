"""HTML link parser for extracting links from HTML files."""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Link:
    """Represents a link found in an HTML file."""
    url: str
    source_file: Path
    line_number: int
    tag: str
    attribute: str

    def is_external(self) -> bool:
        """Check if the link is external (has a scheme)."""
        return bool(urlparse(self.url).scheme)

    def is_fragment_only(self) -> bool:
        """Check if the link is only a fragment (e.g., #section)."""
        return self.url.startswith("#")

    def resolve(self, base_dir: Path) -> Path:
        """Resolve the link to a local file path."""
        if self.is_external() or self.is_fragment_only():
            raise ValueError(f"Cannot resolve external or fragment-only link: {self.url}")

        parsed = urlparse(self.url)
        path = Path(parsed.path)

        if path.is_absolute():
            return base_dir / path.relative_to("/")
        else:
            return (self.source_file.parent / path).resolve()


def extract_links(html_content: str, source_file: Path) -> Iterator[Link]:
    """
    Extract all links from HTML content.

    Args:
        html_content: The HTML content to parse
        source_file: The source file path (for line numbers)

    Yields:
        Link objects for each link found
    """
    lines = html_content.splitlines()

    # Patterns for different link types
    patterns = [
        # <a href="..."> or <a href='...'>
        (r'<a\s+[^>]*href\s*=\s*["\']([^"\']*)["\']', "a", "href"),
        # <link href="..."> or <link href='...'>
        (r'<link\s+[^>]*href\s*=\s*["\']([^"\']*)["\']', "link", "href"),
        # <img src="..."> or <img src='...'>
        (r'<img\s+[^>]*src\s*=\s*["\']([^"\']*)["\']', "img", "src"),
        # <script src="..."> or <script src='...'>
        (r'<script\s+[^>]*src\s*=\s*["\']([^"\']*)["\']', "script", "src"),
        # <iframe src="..."> or <iframe src='...'>
        (r'<iframe\s+[^>]*src\s*=\s*["\']([^"\']*)["\']', "iframe", "src"),
        # <source src="..."> or <source src='...'>
        (r'<source\s+[^>]*src\s*=\s*["\']([^"\']*)["\']', "source", "src"),
        # <video src="..."> or <video src='...'>
        (r'<video\s+[^>]*src\s*=\s*["\']([^"\']*)["\']', "video", "src"),
        # <audio src="..."> or <audio src='...'>
        (r'<audio\s+[^>]*src\s*=\s*["\']([^"\']*)["\']', "audio", "src"),
        # <embed src="..."> or <embed src='...'>
        (r'<embed\s+[^>]*src\s*=\s*["\']([^"\']*)["\']', "embed", "src"),
        # <object data="..."> or <object data='...'>
        (r'<object\s+[^>]*data\s*=\s*["\']([^"\']*)["\']', "object", "data"),
    ]

    for line_num, line in enumerate(lines, start=1):
        for pattern, tag, attr in patterns:
            for match in re.finditer(pattern, line, re.IGNORECASE):
                url = match.group(1)
                # Skip empty URLs, javascript: links, mailto:, tel:, and data: URIs
                if url and not url.startswith(("javascript:", "mailto:", "tel:", "data:")):
                    yield Link(
                        url=url,
                        source_file=source_file,
                        line_number=line_num,
                        tag=tag,
                        attribute=attr
                    )


def find_html_files(root_dir: Path) -> Iterator[Path]:
    """Find all HTML files in a directory recursively."""
    for path in root_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".html", ".htm"}:
            yield path
