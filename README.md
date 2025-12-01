# Chart Creator

A Python tool for creating candlestick charts with volume indicators from stock data files.

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Virtual Environment

1. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   
   On Windows (PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   On Windows (Command Prompt):
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

### Deactivate Virtual Environment

When you're done working, you can deactivate the virtual environment:
```powershell
deactivate
```

## Usage

### Basic Usage

The script requires a data file in CSV format. See `tqqq.txt` in this repository for the correct format example.

**Command format:**
```powershell
python chart_creator.py <data_file> [years]
```

**Parameters:**
- `<data_file>`: Path to your data file (required)
- `[years]`: Number of years to plot (optional, defaults to 1)

### Example

To generate a chart from `tqqq.txt` showing the last 1 year of data:
```powershell
python chart_creator.py tqqq.txt 1
```

To plot 2 years of data:
```powershell
python chart_creator.py tqqq.txt 2
```

To plot 6 months (0.5 years):
```powershell
python chart_creator.py tqqq.txt 0.5
```

### Data File Format

Your data file should be a CSV file with the following columns:
- `Date`: Date in a format that pandas can parse
- `Time`: Time (optional, not used in chart)
- `Open`: Opening price
- `High`: Highest price
- `Low`: Lowest price
- `Close`: Closing price
- `Vol`: Volume
- `OI`: Open Interest (optional, not used in chart)

**Note:** See `tqqq.txt` in this repository for a reference example of the correct format.

### Output

The script automatically generates an output file with the naming convention:
- Input: `filename.txt` → Output: `filename_chart.png`

For example:
- `tqqq.txt` → `tqqq_chart.png`
- `snp500.txt` → `snp500_chart.png`

The chart includes:
- Candlestick price chart with SMA 150 indicator
- Volume chart below
- Status indicator showing if price is above, below, or on the SMA 150

## Project Structure

- `chart_creator.py` - Main script for creating charts
- `requirements.txt` - Python dependencies
- `tqqq.txt` - Example data file (included in repository)
- `venv/` - Virtual environment directory (excluded from git)

**Note:** `example.py` and `analyze_colors.py` are excluded from version control as they are utility/example scripts.

## Dependencies

- pandas >= 2.0.0
- matplotlib >= 3.7.0
- Pillow >= 10.0.0

## Troubleshooting

**If you get a "command not found" error:**
- Make sure the virtual environment is activated
- Verify you're using the correct Python interpreter: `python --version`

**If you get import errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify the virtual environment is activated

**If the chart doesn't generate:**
- Check that your data file matches the expected format (see `tqqq.txt` for reference)
- Ensure the data file path is correct
- Verify the file has enough data points (at least 150 days for SMA calculation)

