# Broken Link Checker CLI

A local-first Python command-line tool that crawls HTML files and reports broken internal links. Designed for authors and small-business sites — no external network requests, no API keys, no tracking.

## Features

- **Local-only checks** — Validates only internal links (relative paths, site-root paths). External links (http://, https://, mailto:, etc.) are skipped by default.
- **CSV reports** — Machine-readable output for automation and CI/CD pipelines.
- **Comprehensive HTML parsing** — Finds links in `<a>`, `<link>`, `<img>`, `<script>`, `<iframe>`, `<video>`, `<audio>`, `<source>`, `<embed>`, and `<object>` tags.
- **Fragment support** — Validates that anchor links (e.g., `page.html#section`) point to existing `id` or `name` attributes.
- **Zero dependencies** — Only uses `click` for CLI; standard library for everything else.
- **MIT licensed** — Free for personal and commercial use.

## Installation

```bash
pip install broken-link-checker
```

Or install from source:

```bash
git clone https://github.com/dylanasdale/broken-link-checker
cd broken-link-checker
pip install -e .
```

## Usage

```bash
# Check current directory (default)
broken-link-checker

# Check a specific directory
broken-link-checker /path/to/site

# Output CSV to file
broken-link-checker -o report.csv

# Include external links in report
broken-link-checker --include-external

# Include fragment-only links in report
broken-link-checker --include-fragments

# Verbose output with summary
broken-link-checker -v
```

## CSV Output Format

The tool outputs CSV with the following columns:

| Column | Description |
|--------|-------------|
| `source_file` | Path to the HTML file containing the link |
| `line_number` | Line number where the link was found |
| `tag` | HTML tag name (a, link, img, script, etc.) |
| `attribute` | Attribute name (href, src, data) |
| `url` | The link URL as written in the HTML |
| `status` | One of: `ok`, `broken`, `external`, `fragment_only`, `error` |
| `resolved_path` | Absolute path to the target file (if resolved) |
| `error_message` | Details for broken or error links |

## Exit Codes

- `0` — No broken links found
- `1` — One or more broken links found
- `2` — Usage error

## Example

```bash
$ broken-link-checker -v ./my-site
Scanning: /home/user/my-site

Summary:
  OK: 12
  Broken: 2
  External (skipped): 3
  Fragment-only (skipped): 1
  Errors: 0
  Total checked: 18
```

```bash
$ broken-link-checker -o report.csv ./my-site
$ cat report.csv
source_file,line_number,tag,attribute,url,status,resolved_path,error_message
"index.html",5,"a","href","missing.html","broken","/home/user/my-site/missing.html","File not found: /home/user/my-site/missing.html"
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=broken_link_checker

# Lint
ruff check .
ruff format .
```

## Credits

Built by **Asdale Dynamics, LLC** — beginner-friendly AI education, books, guides, and practical tools.

- Founder: Dylan Asdale (RN → AI author)
- Book: *The Massive AI Manual*
- Hub: [dylanasdale.github.io](https://dylanasdale.github.io)

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Asdale Dynamics, LLC