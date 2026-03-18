"""Command-line interface for DeepGuard."""

import json
import sys
import webbrowser
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from deepguard.analyzer import ForensicAnalyzer
from deepguard.report import ReportGenerator
from deepguard.utils import is_supported_format

console = Console()


@click.group()
def main():
    """DeepGuard - Offline image forensics and deepfake detection."""
    pass


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output HTML report path",
    default=None,
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["html", "json"]),
    default="html",
    help="Output format",
)
@click.option(
    "--open/--no-open",
    default=True,
    help="Open report in browser",
)
def analyze(file_path: str, output: Optional[str], format: str, open: bool):
    """Analyze a single image for forensic evidence.

    FILE_PATH: Path to the image to analyze
    """
    if not is_supported_format(file_path):
        console.print(
            "[red]Error:[/red] Unsupported file format. "
            "Supported: JPEG, PNG, TIFF, BMP, WebP, PDF"
        )
        sys.exit(1)

    analyzer = ForensicAnalyzer()
    generator = ReportGenerator()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Analyzing image...", total=None)

        try:
            report = analyzer.analyze(file_path)
            progress.stop()
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error analyzing image:[/red] {str(e)}")
            sys.exit(1)

    # Display results
    console.print()
    console.print(f"[bold cyan]Analysis Complete[/bold cyan]")
    console.print(f"[yellow]Overall Verdict:[/yellow] [bold]{report.overall_verdict.value}[/bold]")
    console.print(f"[yellow]Confidence:[/yellow] {report.confidence_score:.1f}%")
    console.print(f"[yellow]Processing Time:[/yellow] {report.processing_time_ms:.2f}ms")
    console.print()

    # Display technique results
    table = Table(title="Technique Results")
    table.add_column("Technique", style="cyan")
    table.add_column("Verdict", style="magenta")
    table.add_column("Confidence", justify="right")

    for name, technique in report.techniques.items():
        table.add_row(
            technique.name,
            technique.verdict,
            f"{technique.confidence:.1f}%",
        )

    console.print(table)
    console.print()

    # Generate report
    if format == "html":
        if output is None:
            output = Path(file_path).stem + "_deepguard_report.html"

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Generating HTML report...", total=None)

            try:
                generator.save_html(report, output, file_path)
                progress.stop()
            except Exception as e:
                progress.stop()
                console.print(f"[red]Error generating report:[/red] {str(e)}")
                sys.exit(1)

        console.print(f"[green]Report saved to:[/green] [bold]{output}[/bold]")

        if open:
            webbrowser.open(f"file://{Path(output).absolute()}")
            console.print("[green]Opening report in browser...[/green]")

    elif format == "json":
        if output is None:
            output = Path(file_path).stem + "_deepguard_report.json"

        try:
            generator.save_json(report, output)
            console.print(f"[green]JSON report saved to:[/green] [bold]{output}[/bold]")
        except Exception as e:
            console.print(f"[red]Error saving JSON:[/red] {str(e)}")
            sys.exit(1)


@main.command()
@click.argument("folder_path", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="deepguard_batch_results.json",
    help="Output JSON file",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Analyze subdirectories recursively",
)
def batch(folder_path: str, output: str, recursive: bool):
    """Analyze all images in a folder."""
    analyzer = ForensicAnalyzer()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Analyzing images...", total=None)

        try:
            reports = analyzer.batch_analyze(folder_path, recursive=recursive)
            progress.stop()
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error:[/red] {str(e)}")
            sys.exit(1)

    console.print(f"[green]Analyzed {len(reports)} images[/green]")

    # Save results
    try:
        with open(output, "w") as f:
            json.dump(
                [report.to_dict() for report in reports],
                f,
                indent=2,
            )
        console.print(f"[green]Results saved to:[/green] [bold]{output}[/bold]")
    except Exception as e:
        console.print(f"[red]Error saving results:[/red] {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output HTML file",
)
def report(file_path: str, output: Optional[str]):
    """Generate a forensic report for an image."""
    if not is_supported_format(file_path):
        console.print(
            "[red]Error:[/red] Unsupported file format. "
            "Supported: JPEG, PNG, TIFF, BMP, WebP, PDF"
        )
        sys.exit(1)

    analyzer = ForensicAnalyzer()
    generator = ReportGenerator()

    if output is None:
        output = Path(file_path).stem + "_report.html"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Creating report...", total=None)

        try:
            report_obj = analyzer.analyze(file_path)
            generator.save_html(report_obj, output, file_path)
            progress.stop()
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error:[/red] {str(e)}")
            sys.exit(1)

    console.print(f"[green]Report saved to:[/green] [bold]{output}[/bold]")


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def metadata(file_path: str, format: str):
    """Extract and display metadata from an image."""
    from deepguard.utils import load_image
    from deepguard.techniques.metadata import MetadataForensics

    if not is_supported_format(file_path):
        console.print(
            "[red]Error:[/red] Unsupported file format. "
            "Supported: JPEG, PNG, TIFF, BMP, WebP, PDF"
        )
        sys.exit(1)

    try:
        image, _ = load_image(file_path)
        metadata_analyzer = MetadataForensics()
        _, metadata = metadata_analyzer.analyze(file_path, image)

        if format == "json":
            console.print(json.dumps({
                "camera_make": metadata.camera_make,
                "camera_model": metadata.camera_model,
                "timestamp": metadata.timestamp,
                "software": metadata.software,
                "orientation": metadata.orientation,
                "width": metadata.width,
                "height": metadata.height,
                "gps_coordinates": metadata.gps_coordinates,
            }, indent=2))
        else:
            table = Table(title="Image Metadata")
            table.add_column("Property", style="cyan")
            table.add_column("Value")

            table.add_row("Camera Make", metadata.camera_make or "Not found")
            table.add_row("Camera Model", metadata.camera_model or "Not found")
            table.add_row("Timestamp", metadata.timestamp or "Not found")
            table.add_row("Software", metadata.software or "Not found")
            table.add_row("Orientation", str(metadata.orientation))
            table.add_row("Width", str(metadata.width))
            table.add_row("Height", str(metadata.height))
            table.add_row("GPS", str(metadata.gps_coordinates) or "Not found")

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output HTML file",
)
def compare(file1: str, file2: str, output: Optional[str]):
    """Compare two images forensically."""
    if not is_supported_format(file1) or not is_supported_format(file2):
        console.print(
            "[red]Error:[/red] Unsupported file format. "
            "Supported: JPEG, PNG, TIFF, BMP, WebP, PDF"
        )
        sys.exit(1)

    analyzer = ForensicAnalyzer()

    if output is None:
        output = "comparison_report.html"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Analyzing images...", total=None)

        try:
            report1 = analyzer.analyze(file1)
            report2 = analyzer.analyze(file2)
            progress.stop()
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error:[/red] {str(e)}")
            sys.exit(1)

    console.print()
    console.print(f"[yellow]Image 1:[/yellow] [bold]{Path(file1).name}[/bold]")
    console.print(f"  Verdict: {report1.overall_verdict.value} ({report1.confidence_score:.1f}%)")

    console.print(f"[yellow]Image 2:[/yellow] [bold]{Path(file2).name}[/bold]")
    console.print(f"  Verdict: {report2.overall_verdict.value} ({report2.confidence_score:.1f}%)")

    console.print(f"[green]Comparison report saved to:[/green] [bold]{output}[/bold]")


if __name__ == "__main__":
    main()
