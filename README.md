# Regulations.gov Comment Downloader

A Python script to download public comments (and PDFs) for any docket on [regulations.gov](https://www.regulations.gov).

## 🔧 Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🔐 API Key Setup

This script requires an API key from [regulations.gov](https://open.gsa.gov/api/regulationsgov/).

### ✅ To get your key:
1. Visit the [Regulations.gov API Key Request Form](https://open.gsa.gov/api/regulationsgov/#getting-started)
2. Fill out your email and click "Request API Key"
3. Check your inbox and copy your new key

### 🔧 How to use your key (Option 1: .env file)
Create a file named `.env` in the project folder and add:

```env
API_KEY=your-key-here
```

Then run the script as normal.

---

## 🚀 Usage

```bash
python comment_scraper.py --docket-id DHS-2025-0013
```

This will:
- Fetch 3 pages (750 comments max) per hour
- Download PDFs for comments that say "See attached file"
- Save a combined deduplicated `DHS-2025-0013_master.csv`

---

## 📂 Output

Each batch appends new comments to:

```
DHS-2025-0013_batches/
├── DHS-2025-0013_master.csv
└── attachments/
    ├── comment123_attachment1.pdf
```

The script will resume automatically and avoid duplicates.

---

## 🕒 API Rate Limits

The script is designed to stay within the 1000 API calls/hour limit by:
- Fetching 3 pages per hour (750 comments max)
- Skipping any previously downloaded comment IDs

You can adjust `PAGES_PER_HOUR` in the script if needed.
