# EIA Crude Oil Inventories Report Automation

## Overview

This Python script automates the process of downloading, processing, and comparing the EIA Crude Oil Inventories report. The script fetches data from the EIA website, processes CSV and PDF files, and extracts relevant information about this week's change in inventories.

## Features
* Downloads CSV and PDF reports from the EIA website.
* Processes and saves the CSV data locally.
* Extracts and prints a summary from the PDF report.
* Generates and saves an image from the PDF overview.

## Requirements
*	Python 3.x
* PyMuPDF (also known as fitz)
* sched

## Usage

#### 1. Configure the next runtime
Update the next_runtime variable in the __main__ section to the next report date and time. Check the report schedule at https://www.eia.gov/petroleum/supply/weekly/schedule.php

```python
next_runtime = datetime.datetime(2024, 6, 20, hour=10, minute=30)
```

#### 2. Run the script
Run the script some time before the report is set to be released. The scheduler will take care of triggering the download attempts automatically. The countdown to the next runtime is displayed in the console.


## Notes
Ensure that your system clock is synchronized.

## License

This script is provided “as is”, without warranty of any kind. Use it at your own risk.