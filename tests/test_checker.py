"""Tests for the link checker."""

import tempfile
from pathlib import Path

from broken_link_checker.checker import LinkStatus, check_directory, check_link
from broken_link_checker.parser import Link


class TestCheckLink:
    """Tests for the check_link function."""

    def test_check_existing_file(self) -> None:
        """Test checking a link to an existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target.html"
            target.write_text("<html><body>Target</body></html>")

            link = Link(
                url="target.html",
                source_file=root / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.OK
            assert result.resolved_path == target

    def test_check_broken_file(self) -> None:
        """Test checking a link to a non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            link = Link(
                url="missing.html",
                source_file=root / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.BROKEN
            assert "not found" in (result.error_message or "")

    def test_check_external_link(self) -> None:
        """Test checking an external link (skipped)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            link = Link(
                url="https://example.com",
                source_file=root / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.EXTERNAL

    def test_check_fragment_only(self) -> None:
        """Test checking a fragment-only link (skipped)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            link = Link(
                url="#section",
                source_file=root / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.FRAGMENT_ONLY

    def test_check_fragment_in_existing_file(self) -> None:
        """Test checking a link with fragment that exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target.html"
            target.write_text('<html><body><div id="section">Content</div></body></html>')

            link = Link(
                url="target.html#section",
                source_file=root / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.OK

    def test_check_fragment_not_in_file(self) -> None:
        """Test checking a link with fragment that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target.html"
            target.write_text("<html><body><div id='other'>Content</div></body></html>")

            link = Link(
                url="target.html#missing",
                source_file=root / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.BROKEN
            assert "not found" in (result.error_message or "")

    def test_check_absolute_path(self) -> None:
        """Test checking a link with absolute path from site root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "page.html"
            target.write_text("<html></html>")

            link = Link(
                url="/page.html",
                source_file=root / "subdir" / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.OK
            assert result.resolved_path == target

    def test_check_image_link(self) -> None:
        """Test checking an image link."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            img = root / "image.png"
            img.write_bytes(b"fake image data")

            link = Link(
                url="image.png",
                source_file=root / "index.html",
                line_number=1,
                tag="img",
                attribute="src"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.OK

    def test_check_css_link(self) -> None:
        """Test checking a CSS link."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            css = root / "style.css"
            css.write_text("body {}")

            link = Link(
                url="style.css",
                source_file=root / "index.html",
                line_number=1,
                tag="link",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.OK

    def test_check_mailto_link(self) -> None:
        """Test checking a mailto: link (treated as external)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            link = Link(
                url="mailto:author@example.com",
                source_file=root / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.EXTERNAL

    def test_check_tel_link(self) -> None:
        """Test checking a tel: link (treated as external)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            link = Link(
                url="tel:+15551234567",
                source_file=root / "index.html",
                line_number=1,
                tag="a",
                attribute="href"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.EXTERNAL

    def test_check_data_uri(self) -> None:
        """Test checking a data: URI (treated as external)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            link = Link(
                url="data:image/png;base64,abc",
                source_file=root / "index.html",
                line_number=1,
                tag="img",
                attribute="src"
            )

            result = check_link(link, root)

            assert result.status == LinkStatus.EXTERNAL


class TestCheckDirectory:
    """Tests for the check_directory function."""

    def test_check_directory_with_broken_links(self) -> None:
        """Test checking a directory with broken links."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create index.html with a broken link
            (root / "index.html").write_text(
                '<html><body><a href="missing.html">Broken</a></body></html>'
            )

            results = list(check_directory(root))

            assert len(results) == 1
            assert results[0].status == LinkStatus.BROKEN

    def test_check_directory_with_working_links(self) -> None:
        """Test checking a directory with working links."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create target file
            (root / "target.html").write_text("<html><body>Target</body></html>")
            # Create index.html with working link
            (root / "index.html").write_text(
                '<html><body><a href="target.html">Working</a></body></html>'
            )

            results = list(check_directory(root))

            assert len(results) == 1
            assert results[0].status == LinkStatus.OK

    def test_check_directory_multiple_files(self) -> None:
        """Test checking multiple HTML files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "index.html").write_text(
                '<html><body><a href="page1.html">Page 1</a></body></html>'
            )
            (root / "page1.html").write_text(
                '<html><body><a href="page2.html">Page 2</a></body></html>'
            )
            (root / "page2.html").write_text("<html><body>End</body></html>")

            results = list(check_directory(root))

            assert len(results) == 2
            assert all(r.status == LinkStatus.OK for r in results)

    def test_check_directory_nested(self) -> None:
        """Test checking nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "index.html").write_text(
                '<html><body><a href="sub/page.html">Sub Page</a></body></html>'
            )
            (root / "sub").mkdir()
            (root / "sub" / "page.html").write_text("<html><body>Sub</body></html>")

            results = list(check_directory(root))

            assert len(results) == 1
            assert results[0].status == LinkStatus.OK

    def test_check_directory_external_links_skipped(self) -> None:
        """Test that external links are skipped by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "index.html").write_text(
                '<html><body><a href="https://example.com">External</a></body></html>'
            )

            results = list(check_directory(root))

            assert len(results) == 1
            assert results[0].status == LinkStatus.EXTERNAL

    def test_check_directory_fragment_only_skipped(self) -> None:
        """Test that fragment-only links are skipped by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "index.html").write_text(
                '<html><body><a href="#top">Top</a></body></html>'
            )

            results = list(check_directory(root))

            assert len(results) == 1
            assert results[0].status == LinkStatus.FRAGMENT_ONLY

    def test_check_directory_invalid_encoding(self) -> None:
        """Test handling of files with invalid encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create a file with invalid UTF-8
            bad_file = root / "bad.html"
            bad_file.write_bytes(b"<html>\xff</html>")

            results = list(check_directory(root))

            # Should handle gracefully (errors='ignore' in read_text)
            assert len(results) == 0

    def test_check_directory_htm_extension(self) -> None:
        """Test that .htm files are also checked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "index.htm").write_text(
                '<html><body><a href="page.html">Link</a></body></html>'
            )
            (root / "page.html").write_text("<html><body>Page</body></html>")

            results = list(check_directory(root))

            assert len(results) == 1
            assert results[0].status == LinkStatus.OK
