"""Example: Analyze a single image file."""

from pathlib import Path

from deepguard.analyzer import ForensicAnalyzer
from deepguard.report import ReportGenerator


def main():
    """Analyze a single image and generate a report."""
    # Path to image file
    image_path = "sample_image.jpg"

    # Check if file exists
    if not Path(image_path).exists():
        print(f"Error: File not found: {image_path}")
        print("Please provide a valid image path.")
        return

    # Create analyzer
    analyzer = ForensicAnalyzer()

    # Analyze image
    print(f"Analyzing {image_path}...")
    report = analyzer.analyze(image_path)

    # Display results
    print(f"\nAnalysis Complete!")
    print(f"Overall Verdict: {report.overall_verdict.value}")
    print(f"Confidence Score: {report.confidence_score:.1f}%")
    print(f"Processing Time: {report.processing_time_ms:.2f}ms")

    # Display technique results
    print("\nTechnique Results:")
    for name, technique in report.techniques.items():
        print(f"  {technique.name}: {technique.verdict} ({technique.confidence:.1f}%)")

    # Generate HTML report
    generator = ReportGenerator()
    output_path = Path(image_path).stem + "_deepguard_report.html"

    print(f"\nGenerating HTML report: {output_path}")
    generator.save_html(report, output_path, image_path)

    print(f"Report saved to: {output_path}")

    # Generate JSON report
    json_output = Path(image_path).stem + "_deepguard_report.json"
    generator.save_json(report, json_output)
    print(f"JSON report saved to: {json_output}")


if __name__ == "__main__":
    main()
