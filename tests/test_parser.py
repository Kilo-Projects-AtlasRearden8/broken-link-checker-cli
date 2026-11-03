"""Tests for the HTML link parser."""

import tempfile
from pathlib import Path

import pytest

from broken_link_checker.parser import Link, extract_links, find_html_files


class TestExtractLinks:
    """Tests for the extract_links function."""

    def test_extract_anchor_links(self) -> None:
        """Test extracting standard anchor links."""
        html = '<a href="page.html">Link</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "page.html"
        assert links[0].tag == "a"
        assert links[0].attribute == "href"
        assert links[0].line_number == 1

    def test_extract_anchor_links_single_quotes(self) -> None:
        """Test extracting anchor links with single quotes."""
        html = "<a href='page.html'>Link</a>"
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "page.html"

    def test_extract_multiple_links(self) -> None:
        """Test extracting multiple links from one line."""
        html = '<a href="page1.html">One</a> <a href="page2.html">Two</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 2
        assert links[0].url == "page1.html"
        assert links[1].url == "page2.html"

    def test_extract_link_tags(self) -> None:
        """Test extracting link tags (stylesheets, etc.)."""
        html = '<link href="style.css" rel="stylesheet">'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "style.css"
        assert links[0].tag == "link"
        assert links[0].attribute == "href"

    def test_extract_img_src(self) -> None:
        """Test extracting image sources."""
        html = '<img src="image.png" alt="Image">'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "image.png"
        assert links[0].tag == "img"
        assert links[0].attribute == "src"

    def test_extract_script_src(self) -> None:
        """Test extracting script sources."""
        html = '<script src="app.js"></script>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "app.js"
        assert links[0].tag == "script"
        assert links[0].attribute == "src"

    def test_extract_iframe_src(self) -> None:
        """Test extracting iframe sources."""
        html = '<iframe src="embed.html"></iframe>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "embed.html"
        assert links[0].tag == "iframe"
        assert links[0].attribute == "src"

    def test_extract_video_src(self) -> None:
        """Test extracting video sources."""
        html = '<video src="movie.mp4"></video>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "movie.mp4"
        assert links[0].tag == "video"

    def test_extract_audio_src(self) -> None:
        """Test extracting audio sources."""
        html = '<audio src="sound.mp3"></audio>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "sound.mp3"
        assert links[0].tag == "audio"

    def test_extract_source_src(self) -> None:
        """Test extracting source sources."""
        html = '<source src="video.webm" type="video/webm">'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "video.webm"
        assert links[0].tag == "source"

    def test_extract_embed_src(self) -> None:
        """Test extracting embed sources."""
        html = '<embed src="plugin.swf">'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "plugin.swf"
        assert links[0].tag == "embed"

    def test_extract_object_data(self) -> None:
        """Test extracting object data."""
        html = '<object data="content.pdf"></object>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "content.pdf"
        assert links[0].tag == "object"
        assert links[0].attribute == "data"

    def test_skip_external_links(self) -> None:
        """Test that external links are still extracted (but marked as external)."""
        html = '<a href="https://example.com">External</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "https://example.com"
        assert links[0].is_external()

    def test_skip_javascript_links(self) -> None:
        """Test that javascript: links are skipped."""
        html = '<a href="javascript:void(0)">JS Link</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 0

    def test_skip_empty_href(self) -> None:
        """Test that empty hrefs are skipped."""
        html = '<a href="">Empty</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 0

    def test_line_numbers(self) -> None:
        """Test that line numbers are correctly tracked."""
        html = """<html>
<body>
<a href="page1.html">Link 1</a>
<a href="page2.html">Link 2</a>
</body>
</html>"""
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 2
        assert links[0].line_number == 3
        assert links[1].line_number == 4

    def test_fragment_links(self) -> None:
        """Test that fragment-only links are extracted."""
        html = '<a href="#section">Section</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "#section"
        assert links[0].is_fragment_only()

    def test_link_with_fragment(self) -> None:
        """Test links with fragments are extracted."""
        html = '<a href="page.html#section">Link</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "page.html#section"
        assert not links[0].is_fragment_only()
        assert not links[0].is_external()

    def test_case_insensitive_tags(self) -> None:
        """Test that tag matching is case-insensitive."""
        html = '<A HREF="page.html">Link</A>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "page.html"

    def test_attributes_with_extra_spaces(self) -> None:
        """Test handling of extra spaces in attributes."""
        html = '<a  href = "page.html" >Link</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "page.html"

    def test_skip_mailto_links(self) -> None:
        """Test that mailto: links are skipped."""
        html = '<a href="mailto:author@example.com">Email</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 0

    def test_skip_tel_links(self) -> None:
        """Test that tel: links are skipped."""
        html = '<a href="tel:+15551234567">Call</a>'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 0

    def test_skip_data_uris(self) -> None:
        """Test that data: URIs are skipped."""
        # 1x1 transparent PNG base64 (split for line length)
        data_uri = (
            "data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        html = f'<img src="{data_uri}" alt="Pixel">'
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 0

    def test_skip_mixed_special_links(self) -> None:
        """Test that javascript:, mailto:, tel:, and data: are all skipped."""
        html = '''
        <a href="javascript:void(0)">JS</a>
        <a href="mailto:test@example.com">Email</a>
        <a href="tel:+15551234567">Call</a>
        <img src="data:image/png;base64,abc">
        <a href="page.html">Real Link</a>
        '''
        links = list(extract_links(html, Path("index.html")))

        assert len(links) == 1
        assert links[0].url == "page.html"


class TestFindHtmlFiles:
    """Tests for the find_html_files function."""

    def test_find_html_files(self) -> None:
        """Test finding HTML files in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "index.html").write_text("<html></html>")
            (root / "page.htm").write_text("<html></html>")
            (root / "subdir").mkdir()
            (root / "subdir" / "nested.html").write_text("<html></html>")
            (root / "readme.txt").write_text("text")

            files = list(find_html_files(root))

            assert len(files) == 3
            names = {f.name for f in files}
            assert names == {"index.html", "page.htm", "nested.html"}

    def test_find_no_html_files(self) -> None:
        """Test finding no HTML files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "readme.txt").write_text("text")

            files = list(find_html_files(root))

            assert len(files) == 0


class TestLinkDataclass:
    """Tests for the Link dataclass."""

    def test_is_external(self) -> None:
        """Test is_external method."""
        link = Link(
            url="https://example.com",
            source_file=Path("index.html"),
            line_number=1,
            tag="a",
            attribute="href"
        )
        assert link.is_external()

    def test_is_not_external(self) -> None:
        """Test is_external for relative links."""
        link = Link(
            url="page.html",
            source_file=Path("index.html"),
            line_number=1,
            tag="a",
            attribute="href"
        )
        assert not link.is_external()

    def test_is_fragment_only(self) -> None:
        """Test is_fragment_only method."""
        link = Link(
            url="#section",
            source_file=Path("index.html"),
            line_number=1,
            tag="a",
            attribute="href"
        )
        assert link.is_fragment_only()

    def test_is_not_fragment_only(self) -> None:
        """Test is_fragment_only for non-fragment links."""
        link = Link(
            url="page.html#section",
            source_file=Path("index.html"),
            line_number=1,
            tag="a",
            attribute="href"
        )
        assert not link.is_fragment_only()

    def test_resolve_relative(self) -> None:
        """Test resolving relative links."""
        link = Link(
            url="subdir/page.html",
            source_file=Path("/root/index.html"),
            line_number=1,
            tag="a",
            attribute="href"
        )
        resolved = link.resolve(Path("/root"))
        assert resolved == Path("/root/subdir/page.html")

    def test_resolve_absolute(self) -> None:
        """Test resolving absolute links (from site root)."""
        link = Link(
            url="/page.html",
            source_file=Path("/root/subdir/index.html"),
            line_number=1,
            tag="a",
            attribute="href"
        )
        resolved = link.resolve(Path("/root"))
        assert resolved == Path("/root/page.html")

    def test_resolve_external_raises(self) -> None:
        """Test that resolving external links raises ValueError."""
        link = Link(
            url="https://example.com",
            source_file=Path("index.html"),
            line_number=1,
            tag="a",
            attribute="href"
        )
        with pytest.raises(ValueError):
            link.resolve(Path())

    def test_resolve_fragment_raises(self) -> None:
        """Test that resolving fragment-only links raises ValueError."""
        link = Link(
            url="#section",
            source_file=Path("index.html"),
            line_number=1,
            tag="a",
            attribute="href"
        )
        with pytest.raises(ValueError):
            link.resolve(Path())
