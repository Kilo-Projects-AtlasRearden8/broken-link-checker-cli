# STATUS: Broken Link Checker CLI

## What Was Built

A complete Python CLI tool (`broken-link-checker`) that crawls local HTML files and reports broken internal links. Designed for authors and small-business sites with a local-first, no-keys approach.

### Core Components

1. **Link Parser** (`src/broken_link_checker/parser.py`)
   - Extracts links from HTML using regex patterns
   - Supports 10 HTML tag types: `<a>`, `<link>`, `<img>`, `<script>`, `<iframe>`, `<video>`, `<audio>`, `<source>`, `<embed>`, `<object>`
   - Handles both single and double quotes, case-insensitive tags, extra whitespace
   - Tracks line numbers for precise reporting
   - Identifies and skips external links, fragment-only links, javascript:, mailto:, tel:, and data: URIs

2. **Link Checker** (`src/broken_link_checker/checker.py`)
   - Validates local file references only (no network requests)
   - Resolves relative paths, site-root absolute paths (`/path`), and fragment links
   - Checks fragment existence by looking for `id` or `name` attributes in target files
   - Handles encoding errors gracefully with `errors="ignore"`
   - Treats mailto:, tel:, and data: URIs as external (skipped by default)

3. **CLI Interface** (`src/broken_link_checker/cli.py`)
   - Built with Click for robust argument parsing
   - CSV output to stdout or file (`-o/--output`)
   - Options to include external links (`--include-external`) and fragment-only links (`--include-fragments`)
   - Verbose mode with summary statistics (`-v/--verbose`)
   - Exit code 1 when broken links found (CI-friendly)

### Test Suite (54 tests, all passing)

- **Parser tests** (33 tests): Link extraction, HTML tag variants, edge cases, Link dataclass methods, mailto:/tel:/data: URI handling
- **Checker tests** (21 tests): File existence, fragments, external links, mailto:/tel:/data: URIs, directory traversal, encoding errors

### Documentation & Licensing

- **MIT LICENSE** with exact copyright: `Copyright (c) 2026 Asdale Dynamics, LLC`
- **README.md** with comprehensive usage examples, CSV format documentation, supported tags table, exit codes, and Asdale Dynamics, LLC credit
- **.gitignore** excluding build artifacts, virtual environments, and test outputs

## How to Run

```bash
# Install (from project root)
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"

# Basic usage
broken-link-checker                    # Check current directory
broken-link-checker /path/to/site      # Check specific directory
broken-link-checker -o report.csv      # Output CSV to file
broken-link-checker -v                 # Verbose with summary
broken-link-checker --include-external # Include external links in report
broken-link-checker --include-fragments # Include fragment-only links in report

# Run tests
pytest -v

# Lint
ruff check .
ruff format .
```

## Verification Results

✅ **All 54 tests pass** (up from 47)  
✅ **Linting clean** (ruff with --fix --unsafe-fixes)  
✅ **CLI works correctly** - tested with comprehensive sample site containing:
- Working relative links (`page.html`)
- Site-root absolute links (`/page.html`)
- Broken links (`missing.html`)
- External HTTPS links (skipped by default)
- mailto: and tel: links (skipped by default)
- Fragment-only links (skipped by default)
- Links with fragments (`page.html#section`) - validated
- Data URIs (skipped by default)
- Image, CSS, and script references
- Video, audio, iframe, embed, object, source tags
- Nested directories

✅ **CSV output verified** - proper format with all 8 columns  
✅ **Exit codes correct** - returns 1 when broken links found, 0 otherwise  
✅ **No external dependencies** beyond Click (stdlib for everything else)  
✅ **No secrets, API keys, or personal data** in any files  
✅ **No GitHub Actions / .github/workflows files**  
✅ **MIT License** with exact required copyright line  
✅ **Asdale Dynamics, LLC credited** in README and LICENSE  
✅ **Git initialized** with 3 commits (initial, .gitignore, improvements)

## Known Gaps / Future Improvements

1. **No HTML parser library** - Uses regex which may miss malformed HTML edge cases (by design for zero heavy dependencies)
2. **No parallel processing** - Single-threaded; could be faster for large sites
3. **No config file support** - All options via CLI flags only
4. **No ignore patterns** - Cannot exclude specific files/directories from checking
5. **Fragment checking limited** - Only checks `id` and `name` attributes; doesn't parse complex JS-generated anchors
6. **No Windows path testing** - Developed/tested on Linux only
7. **No Python 3.9 support** - Requires 3.10+ (for modern `dataclass` features, `Path` methods)

## Project Structure

```
broken-link-checker-cli/
├── LICENSE
├── README.md
├── pyproject.toml
├── .gitignore
├── src/
│   └── broken_link_checker/
│       ├── __init__.py
│       ├── parser.py      # Link extraction
│       ├── checker.py     # Link validation
│       └── cli.py         # Click CLI
└── tests/
    ├── test_parser.py     # 33 tests
    └── test_checker.py    # 21 tests
```

## License

MIT License - Copyright (c) 2026 Asdale Dynamics, LLC