"""Command-line interface for the broken link checker."""

import csv
import sys
from pathlib import Path

import click

from . import __version__
from .checker import LinkStatus, check_directory


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
)
@click.option(
    "--output", "-o",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    help="Output CSV file path (default: stdout)",
)
@click.option(
    "--include-external/--no-external",
    default=False,
    help="Include external links in report (default: False)",
)
@click.option(
    "--include-fragments/--no-fragments",
    default=False,
    help="Include fragment-only links in report (default: False)",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show progress and summary",
)
@click.version_option(version=__version__, prog_name="broken-link-checker")
def main(
    path: Path,
    output: Path | None,
    include_external: bool,
    include_fragments: bool,
    verbose: bool,
) -> None:
    """
    Check local HTML files for broken links.

    PATH: Directory containing HTML files to check (default: current directory).

    This tool crawls local HTML files and validates internal links only.
    External links (http://, https://, mailto:, etc.) are skipped by default.
    """
    root_dir = path.resolve()

    if verbose:
        click.echo(f"Scanning: {root_dir}", err=True)

    results = list(check_directory(root_dir))

    # Filter results based on options
    filtered_results = []
    for result in results:
        if result.status == LinkStatus.EXTERNAL and not include_external:
            continue
        if result.status == LinkStatus.FRAGMENT_ONLY and not include_fragments:
            continue
        filtered_results.append(result)

    # Write CSV output
    if output:
        outfile = output.open("w", newline="", encoding="utf-8")
        close_file = True
    else:
        outfile = sys.stdout
        close_file = False

    try:
        writer = csv.writer(outfile)
        writer.writerow([
            "source_file",
            "line_number",
            "tag",
            "attribute",
            "url",
            "status",
            "resolved_path",
            "error_message"
        ])

        for result in filtered_results:
            writer.writerow([
                str(result.link.source_file),
                result.link.line_number,
                result.link.tag,
                result.link.attribute,
                result.link.url,
                result.status.value,
                str(result.resolved_path) if result.resolved_path else "",
                result.error_message or ""
            ])
    finally:
        if close_file:
            outfile.close()

    # Print summary if verbose
    if verbose:
        broken = sum(1 for r in filtered_results if r.status == LinkStatus.BROKEN)
        ok = sum(1 for r in filtered_results if r.status == LinkStatus.OK)
        external = sum(1 for r in filtered_results if r.status == LinkStatus.EXTERNAL)
        fragments = sum(1 for r in filtered_results if r.status == LinkStatus.FRAGMENT_ONLY)
        errors = sum(1 for r in filtered_results if r.status == LinkStatus.ERROR)

        click.echo("\nSummary:", err=True)
        click.echo(f"  OK: {ok}", err=True)
        click.echo(f"  Broken: {broken}", err=True)
        click.echo(f"  External (skipped): {external}", err=True)
        click.echo(f"  Fragment-only (skipped): {fragments}", err=True)
        click.echo(f"  Errors: {errors}", err=True)
        click.echo(f"  Total checked: {len(filtered_results)}", err=True)

    # Exit with error code if broken links found
    if any(r.status == LinkStatus.BROKEN for r in filtered_results):
        sys.exit(1)


if __name__ == "__main__":
    main()
