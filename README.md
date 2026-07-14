# Root Measure LR

Based on Root Measure from Will in the Dinneny Lab

Updated to include lateral root counting.

Desktop app for measuring root lengths from scanned agar plate images.

Point-and-click each seedling on a scan, and Root Measure traces the root, measures its length in centimeters, and writes tidy CSV output ready for analysis. Supports batches of images, multi-plate scans, genotype/treatment labels, per-plate thresholds, and full session save/resume.

## Features

- Multi-plate scans: select plate corners on each image, then click roots one-by-one
- Automatic root tracing via skeleton graphs (OpenCV + scikit-image + networkx)
- Manual retrace and re-click for tricky roots
- Per-image genotype/treatment labels, per-plate thresholds
- CSV output (raw + tidy) plus box plots with statistics (ANOVA / t-test / Tukey / CLD)
- Session save/resume — pick up mid-batch without losing clicks
- Cross-platform: macOS (Apple Silicon and Intel) and Windows 10+

## Installation

Requires macOS or Windows 10+. The installer sets up Python 3.12, dependencies, and the app automatically.

**macOS** — open Terminal and paste:
```bash
sudo curl -sL https://raw.githubusercontent.com/williangviana/root-measure/stable/install/install.sh | bash
```

**Windows** — open PowerShell and paste:
```powershell
powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/williangviana/root-measure/stable/install/install.ps1 | iex"
```

After installation:
- **macOS** — launch *Root Measure* from Applications or Launchpad
- **Windows** — use the *Root Measure* shortcut on your Desktop

## Workflow

1. **Folder** — pick the folder of scanned plate images
2. **Images** — review the image list; drop or reorder as needed
3. **Settings** — set experiment name, plate count per scan, threshold defaults
4. **Experiment** — assign genotype/treatment labels per image
5. **Workflow** — for each image:
   - Click plate corners to define the plate region(s)
   - Click each seedling root tip; the app traces the root and records its length
   - Review, re-click, or manually retrace as needed
6. **Save** — CSV output lands in `output/` (raw + tidy); box plot with statistics is written alongside

Progress is auto-saved: closing the app mid-batch and reopening it restores clicks, labels, and thresholds.

## Development

```bash
git clone https://github.com/williangviana/root-measure.git
cd root-measure
python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r install/requirements.txt
python -m gui.app
```

### Project structure

```
root_measure/
├── gui/                   # CustomTkinter desktop app
│   ├── app.py             # Main window, image loading, event routing
│   ├── sidebar.py         # Collapsible workflow sections + progress bar
│   ├── canvas.py          # Plate selection, root clicking, review, zoom
│   └── workflow.py        # Tracing loop, retry, CSV, plotting
├── scripts/               # Shared backend
│   ├── image_processing.py  # Binary root mask
│   ├── plate_detection.py   # Plate ROI detection
│   ├── root_tracing.py      # Tip detection + skeleton graph traversal
│   ├── csv_output.py        # CSV append
│   ├── plotting.py          # Box plots + statistics
│   └── utils.py
├── install/               # Cross-platform installers
└── output/                # CSV results (gitignored)
```

**Stack:** Python 3.12, CustomTkinter, OpenCV, scikit-image, networkx, pandas, SciPy, statsmodels, matplotlib.

## License

See repository for license details.
