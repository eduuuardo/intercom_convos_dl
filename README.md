# Intercom Conversation Downloader

This script automates the download of conversation transcripts from Intercom using URLs provided in an Excel file. Each conversation is saved as a `.txt` file and grouped into `.zip` batches for easier handling.
Note: Chrome for test is required.

## Features

- 📥 Automated conversation downloads from Intercom  
- 📦 Batch processing (default: 100 conversations per batch)  
- 🗜️ Automatic ZIP compression  
- 🔁 Robust error handling with retries and logs  
- 📊 Simple Excel-based input (no need to touch the code)  
- ⏱️ Progress bar with ETA calculation  

## 📋 Requirements

- Python ≥ 3.8  
- Google Chrome browser  
- Dependencies (install with pip):

```bash
pip install playwright pandas openpyxl
playwright install chromium
```

## Usage
1. Go to **Intercom → Reports**.  
2. Drill down into the **"Conversations Replied"** metric and **export the CSV**.  
   - You’ll need the **Conversation ID** from that file.
3. Prepare your Excel file:
   - Name it `links.xlsx`
   - Create a sheet named `convos`
   - Add all conversation URLs under a column titled `url`
4. Build each URL like this: https://app.intercom.com/a/inbox/$proyect_id/inbox/conversation/$idConversation
   Replace `$project_id` and `$conversation_id` with the actual values.
6. Save the Excel file in the **same folder** as the script.

## Run the script
1. Launch Chrome with remote debugging:
```
chrome --remote-debugging-port=9222
```
- Run the script
```
python intercom_dump.py
```

## Output
Conversations are saved as .txt files in the downloads folder
Files are grouped into ZIPs: batch_001.zip, batch_002.zip, etc.

📝 Notes
This is my first public project using Playwright and Python!
Feel free to open issues, suggest improvements, or submit PRs to enhance the tool. All feedback is welcome!
