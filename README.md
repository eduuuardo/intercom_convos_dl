# Description
This script automates downloading conversation transcripts from Intercom based on provided conversation URLs stored in an Excel file. It saves each conversation as a .txt file and bundles them into ZIP batches for easy handling.

# Features
- Automated conversation downloads from Intercom
- Batch processing (default: 100 conversations per batch)
- Automatic ZIP compression of batches
- Robust error handling with retries and logs
- Simple Excel-based input for URLs
- Progress bar and ETA calculation

# Requirements
- Python ≥ 3.8
- Chrome browser
- Dependencies (install via pip):

```bash
pip install playwright pandas openpyxl
playwright install chromium
```

# Usage
Prepare your Excel file:
Create an Excel file named links.xlsx.
Add a sheet named convos.
Place all conversation URLs in a column labeled url.
Launch Chrome with remote debugging: `chrome --remote-debugging-port=9222`
Run the script: `python intercom_dump.py`

The downloaded conversations are stored in the downloads folder, compressed into ZIP files (batch_XXX.zip).

# Note
This is my first public project using Playwright and Python!
Feel free to provide feedback, open issues, or submit PRs to enhance functionality, documentation, or code quality. All contributions are welcome! 🌟

