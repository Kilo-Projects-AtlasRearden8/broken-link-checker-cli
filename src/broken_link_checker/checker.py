"""Link checker for validating local file references."""

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .parser import Link, find_html_files


class LinkStatus(Enum):
    """Status of a link check."""
    OK = "ok"
    BROKEN = "broken"
    EXTERNAL = "external"
    FRAGMENT_ONLY = "fragment_only"
    ERROR = "error"


@dataclass(frozen=True)
class CheckResult:
    """Result of checking a single link."""
    link: Link
    status: LinkStatus
    resolved_path: Path | None = None
    error_message: str | None = None


def check_link(link: Link, base_dir: Path) -> CheckResult:
    """
    Check a single link for validity.

    Args:
        link: The link to check
        base_dir: The base directory for resolving relative paths

    Returns:
        CheckResult with the status and any error information
    """
    # External links are skipped (local-only mode)
    if link.is_external():
        return CheckResult(
            link=link,
            status=LinkStatus.EXTERNAL,
            error_message="External link (skipped in local-only mode)"
        )

    # Fragment-only links are skipped
    if link.is_fragment_only():
        return CheckResult(
            link=link,
            status=LinkStatus.FRAGMENT_ONLY,
            error_message="Fragment-only link (skipped)"
        )

    try:
        resolved_path = link.resolve(base_dir)
    except ValueError as e:
        return CheckResult(
            link=link,
            status=LinkStatus.ERROR,
            error_message=str(e)
        )

    # Check if the resolved path exists
    if resolved_path.exists():
        # For fragment links, check if the fragment exists in the file
        parsed = __import__("urllib.parse").parse.urlparse(link.url)
        if parsed.fragment:
            if _check_fragment_exists(resolved_path, parsed.fragment):
                return CheckResult(
                    link=link,
                    status=LinkStatus.OK,
                    resolved_path=resolved_path
                )
            else:
                return CheckResult(
                    link=link,
                    status=LinkStatus.BROKEN,
                    resolved_path=resolved_path,
                    error_message=f"Fragment '#{parsed.fragment}' not found in target file"
                )
        return CheckResult(
            link=link,
            status=LinkStatus.OK,
            resolved_path=resolved_path
        )
    else:
        return CheckResult(
            link=link,
            status=LinkStatus.BROKEN,
            resolved_path=resolved_path,
            error_message=f"File not found: {resolved_path}"
        )


def _check_fragment_exists(file_path: Path, fragment: str) -> bool:
    """Check if a fragment (id or name anchor) exists in an HTML file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        # Check for id="fragment" or name="fragment"
        import re
        pattern = rf'(?:id|name)\s*=\s*["\']{re.escape(fragment)}["\']'
        return bool(re.search(pattern, content, re.IGNORECASE))
    except Exception:
        return False


def check_directory(root_dir: Path) -> Iterator[CheckResult]:
    """
    Check all links in all HTML files in a directory.

    Args:
        root_dir: The root directory to scan

    Yields:
        CheckResult for each link found
    """
    base_dir = root_dir.resolve()

    for html_file in find_html_files(base_dir):
        try:
            content = html_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            yield CheckResult(
                link=Link(
                    url="",
                    source_file=html_file,
                    line_number=0,
                    tag="",
                    attribute=""
                ),
                status=LinkStatus.ERROR,
                error_message=f"Failed to read file: {e}"
            )
            continue

        from .parser import extract_links
        for link in extract_links(content, html_file):
            yield check_link(link, base_dir)
