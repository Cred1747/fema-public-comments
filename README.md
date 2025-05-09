# Regulations.gov Comment Scraper

A Python script to download public comments (and PDFs) for any docket on [regulations.gov](https://www.regulations.gov).

## 🔧 Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
python comment_scraper.py --docket-id DHS-2025-0013
```

## 📂 Output

Each batch (3 pages, 750 comments max) is saved as:

```
DHS-2025-0013_batches/
├── DHS-2025-0013_batch_1.csv
├── DHS-2025-0013_batch_2.csv
└── attachments/
    ├── comment123_attachment1.pdf
```

The script will resume automatically using the `DHS-2025-0013_checkpoint.txt` file.

## 🕒 Respecting API Limits

The script pulls 3 pages per hour (750 comments max), then waits 1 hour before continuing.

## 📌 Notes

- Comments with attachments will download the first available PDF.
- Text-only comments are stored in the `comment` column.
