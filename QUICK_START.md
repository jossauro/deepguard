# DeepGuard - Quick Start Guide

## Installation

```bash
pip install -e .
```

This installs DeepGuard with the `deepguard` command available in your terminal.

## Basic Commands

### 1. Analyze a Single Image

```bash
deepguard analyze photo.jpg
```

This performs complete forensic analysis and opens an interactive HTML report in your browser.

**Options:**
- `--output report.html` - Save to custom location
- `--no-open` - Don't auto-open in browser

### 2. Extract Metadata Only

```bash
deepguard metadata photo.jpg
```

View EXIF data, camera model, software used, GPS coordinates, etc.

**Options:**
- `--format json` - Output as JSON for scripting

### 3. Batch Process Images

```bash
deepguard batch ./evidence_folder --recursive
```

Analyze all images in a folder and save results to JSON.

**Options:**
- `--output results.json` - Custom output file
- `--recursive` / `-r` - Search subdirectories

### 4. Generate HTML Report

```bash
deepguard report suspicious_image.jpg
```

Create a detailed forensic report with visualizations.

### 5. Compare Two Images

```bash
deepguard compare original.jpg edited.jpg
```

Analyze both images and generate side-by-side comparison.

## Understanding the Results

### Verdict Levels

- **AUTHENTIC (Green)** - No obvious signs of manipulation detected
- **SUSPICIOUS (Yellow)** - Some anomalies detected, further investigation recommended
- **MANIPULATED (Red)** - Strong evidence of editing or deepfake artifacts

### Confidence Score

Ranges from 0-100%. Higher means more certain the verdict is correct.

### Forensic Techniques Used

1. **Error Level Analysis (ELA)** - Detects compression inconsistencies from editing
2. **Noise Pattern Analysis** - Finds statistically anomalous noise regions
3. **Metadata Forensics** - Analyzes EXIF data for signs of editing
4. **Copy-Move Detection** - Identifies duplicated/cloned regions
5. **Face Consistency Check** - Analyzes faces for deepfake indicators

## Example Workflows

### Investigation Workflow

```bash
# 1. Quickly check if image is authentic
deepguard analyze suspicious_photo.jpg --no-open

# 2. Extract detailed metadata
deepguard metadata suspicious_photo.jpg --format json > metadata.json

# 3. Compare with reference image
deepguard compare reference.jpg suspicious_photo.jpg
```

### Batch Evidence Analysis

```bash
# Analyze all images in evidence folder
deepguard batch ./evidence/ --recursive --output analysis_results.json

# Check results programmatically
python3 -c "import json; results = json.load(open('analysis_results.json'));
print(f'Analyzed {len(results)} images')"
```

### Report Generation

```bash
# Generate detailed HTML report
deepguard report evidence.jpg --output detailed_report.html

# Open in browser manually
open detailed_report.html  # macOS
xdg-open detailed_report.html  # Linux
start detailed_report.html  # Windows
```

## Output Files

After analysis, you get:

- `report.html` - Interactive forensic report (open in any browser)
- `report.json` - Machine-readable results for automation
- Console output - Immediate verdict and confidence scores

## Tips & Tricks

### Run Silently (No Terminal Output)

```bash
deepguard analyze photo.jpg --no-open 2>/dev/null
```

### Export Results to Database

```bash
deepguard batch ./images --output results.json
# Then import results.json into your database
```

### Compare Multiple Images

```bash
for img in *.jpg; do
    deepguard analyze "$img" --no-open
done
```

### Extract Metadata for All Images

```bash
deepguard batch ./images --output metadata.json
```

## Understanding HTML Reports

The generated HTML report includes:

- **Verdict Badge** - Overall classification with color coding
- **Confidence Meter** - Visual representation of certainty
- **Source Image** - Original image embedded in report
- **Technique Breakdowns** - Individual results from each forensic technique
- **Metadata Table** - All extracted camera and software data
- **Recommendations** - Suggested next steps based on findings
- **Technical Details** - JSON data for each technique

Reports are self-contained (can be emailed as single file).

## Limitations

- Cannot recover original image content
- Cannot identify specific edits, only IF edits occurred
- Works best with well-lit faces (face detection)
- Heavily compressed images may reduce accuracy
- Cannot determine WHEN edits occurred

## For Legal Use

DeepGuard results should be considered one data point among many. For legal proceedings:

1. Have findings verified by professional forensic experts
2. Document all analysis steps
3. Export JSON results for reproducibility
4. Preserve original image files
5. Use HTML report as supporting documentation

## Support

- Check README.md for full documentation
- See examples/analyze_single.py for Python API usage
- Review CONTRIBUTING.md for development setup

## Legal Notice

DeepGuard is a forensic analysis tool for educational and investigative purposes.
Results are probabilistic and not legal proof of tampering.
