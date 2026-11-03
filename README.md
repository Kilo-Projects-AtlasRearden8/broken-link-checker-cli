# Broken Link Checker CLI

A local-first Python command-line tool that crawls HTML files and reports broken internal links. Designed for authors and small-business sites — no external network requests, no API keys, no tracking.

## Why This Tool?

If you're an author with a book website, a small business with a simple HTML site, or anyone who maintains local HTML files, you know the frustration of clicking a link and getting a 404. This tool helps you catch those broken links **before** your visitors do — entirely on your machine, with no data leaving your computer.

## Features

- **Local-only checks** — Validates only internal links (relative paths like `page.html`, site-root paths like `/page.html`). External links (http://, https://, mailto:, tel:, etc.) are skipped by default.
- **CSV reports** — Machine-readable output for automation, CI/CD pipelines, or spreadsheet analysis.
- **Comprehensive HTML parsing** — Finds links in 10 HTML tag types: `<a>`, `<link>`, `<img>`, `<script>`, `<iframe>`, `<video>`, `<audio>`, `<source>`, `<embed>`, and `<object>`.
- **Fragment/anchor support** — Validates that anchor links (e.g., `page.html#section`) point to existing `id` or `name` attributes in the target file.
- **Zero heavy dependencies** — Only uses `click` for the CLI; standard library for everything else.
- **MIT licensed** — Free for personal and commercial use.
- **Cross-platform** — Works on Linux, macOS, and Windows.

## Installation

### From PyPI (when published)
```bash
pip install broken-link-checker
```

### From Source (Recommended for Now)
```bash
git clone https://github.com/dylanasdale/broken-link-checker
cd broken-link-checker
pip install -e .
```

### With Development Dependencies
```bash
pip install -e ".[dev]"
```

This installs `pytest`, `pytest-cov`, and `ruff` for testing and linting.

## Quick Start

```bash
# Check current directory for broken links
broken-link-checker

# Check a specific site directory
broken-link-checker ./my-website

# Save results to CSV for spreadsheet review
broken-link-checker -o broken-links.csv ./my-website

# See a summary of what was checked
broken-link-checker -v ./my-website
```

## Usage Examples

### Basic Check
```bash
$ broken-link-checker ./site
source_file,line_number,tag,attribute,url,status,resolved_path,error_message
"site/index.html",10,"a","href","missing.html","broken","/home/user/site/missing.html","File not found: /home/user/site/missing.html"
```

### Verbose Mode (Human-Friendly Summary)
```bash
$ broken-link-checker -v ./site
Scanning: /home/user/site

Summary:
  OK: 23
  Broken: 2
  External (skipped): 5
  Fragment-only (skipped): 3
  Errors: 0
  Total checked: 33
```

### Include External Links in Report
```bash
# By default, external links are skipped. Use this flag to include them in the CSV.
broken-link-checker --include-external ./site
```

### Include Fragment-Only Links
```bash
# By default, fragment-only links (#section) are skipped. Use this flag to include them.
broken-link-checker --include-fragments ./site
```

### Combine Options
```bash
# Full report with everything, saved to CSV, with summary
broken-link-checker -v --include-external --include-fragments -o full-report.csv ./site
```

## Understanding the CSV Output

The tool outputs CSV with these columns:

| Column | Description |
|--------|-------------|
| `source_file` | Path to the HTML file containing the link |
| `line_number` | Line number where the link was found |
| `tag` | HTML tag name (`a`, `link`, `img`, `script`, etc.) |
| `attribute` | Attribute name (`href`, `src`, `data`) |
| `url` | The link URL exactly as written in the HTML |
| `status` | One of: `ok`, `broken`, `external`, `fragment_only`, `error` |
| `resolved_path` | Absolute path to the target file (if resolved) |
| `error_message` | Human-readable details for broken or error links |

### Status Values Explained

| Status | Meaning |
|--------|---------|
| `ok` | Link points to an existing file (and fragment, if present) |
| `broken` | Link points to a missing file, or fragment doesn't exist in target |
| `external` | Link has a scheme (http://, https://, mailto:, etc.) — skipped by default |
| `fragment_only` | Link is only a fragment (e.g., `#top`) — skipped by default |
| `error` | Something went wrong reading the source file |

## Exit Codes

Use these in scripts and CI/CD:

- `0` — No broken links found (success)
- `1` — One or more broken links found
- `2` — Usage error (invalid arguments, path doesn't exist, etc.)

```bash
# Example: Use in a CI script
if broken-link-checker ./site; then
    echo "All links OK!"
else
    echo "Broken links detected!"
    exit 1
fi
```

## What Links Are Checked?

| Link Type | Example | Checked? |
|-----------|---------|----------|
| Relative file | `page.html`, `../about.html` | ✅ Yes |
| Site-root absolute | `/page.html`, `/assets/style.css` | ✅ Yes |
| Same-page anchor | `#section` | ⚠️ Skipped by default (`--include-fragments`) |
| File with anchor | `page.html#section` | ✅ Yes (file + fragment) |
| External HTTP/HTTPS | `https://example.com` | ⚠️ Skipped by default (`--include-external`) |
| Email links | `mailto:author@example.com` | ⚠️ Skipped by default (`--include-external`) |
| Phone links | `tel:+15551234567` | ⚠️ Skipped by default (`--include-external`) |
| JavaScript | `javascript:void(0)` | ❌ Always skipped |
| Data URIs | `data:image/png;base64,...` | ❌ Always skipped |
| Empty href | `href=""` | ❌ Always skipped |

## Supported HTML Tags & Attributes

| Tag | Attribute | Purpose |
|-----|-----------|---------|
| `<a>` | `href` | Hyperlinks |
| `<link>` | `href` | Stylesheets, preloads, etc. |
| `<img>` | `src` | Images |
| `<script>` | `src` | JavaScript files |
| `<iframe>` | `src` | Embedded pages |
| `<video>` | `src` | Video files |
| `<audio>` | `src` | Audio files |
| `<source>` | `src` | Media sources |
| `<embed>` | `src` | Plugins/embeds |
| `<object>` | `data` | Object data |

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=broken_link_checker --cov-report=term-missing
```

### Linting & Formatting
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Project Structure
```
broken-link-checker/
├── LICENSE
├── README.md
├── pyproject.toml
├── .gitignore
├── src/
│   └── broken_link_checker/
│       ├── __init__.py
│       ├── parser.py      # HTML link extraction
│       ├── checker.py     # Link validation logic
│       └── cli.py         # Click CLI interface
└── tests/
    ├── test_parser.py     # 28 tests for link parsing
    └── test_checker.py    # 19 tests for link checking
```

## How It Works (For Curious Minds)

1. **Discovery** — Recursively finds all `.html` and `.htm` files in the target directory
2. **Parsing** — Uses regex patterns to extract links from 10 HTML tag types, tracking line numbers
3. **Resolution** — Converts relative paths to absolute paths based on the source file's location
4. **Validation** — Checks if the target file exists; for fragments, scans the target file for matching `id` or `name` attributes
5. **Reporting** — Outputs CSV with detailed results; optionally prints a human-friendly summary

**No network requests are ever made.** External links are detected by their URL scheme and simply reported as `external` (or skipped entirely).

## Limitations & Known Gaps

- **Regex-based parsing** — Not a full HTML parser; may miss links in malformed HTML or complex edge cases (by design to avoid heavy dependencies)
- **No parallel processing** — Single-threaded; large sites may take longer
- **No config file** — All options via CLI flags only
- **No ignore patterns** — Cannot exclude specific files/directories from checking
- **Fragment checking** — Only validates static `id`/`name` attributes; won't find dynamically generated anchors
- **No Windows CI** — Developed/tested primarily on Linux

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run `pytest` and `ruff check .`
5. Submit a pull request

## Credits

Built by **Asdale Dynamics, LLC** — beginner-friendly AI education, books, guides, and practical tools.

- Founder: Dylan Asdale (RN → AI author)
- Book: *The Massive AI Manual*
- Hub: [dylanasdale.github.io](https://dylanasdale.github.io)

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Asdale Dynamics, LLC