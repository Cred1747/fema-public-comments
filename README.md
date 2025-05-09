# Regulations.gov Comment Scraper

This Python tool retrieves public comments for **any docket** on [regulations.gov](https://www.regulations.gov) using their v4 API.

It supports:
- Batch downloading of comments (3 pages/hour to respect rate limits)
- Fetching full text from each comment
- Downloading PDF attachments when applicable
- Resuming interrupted downloads via checkpoints

---

## 🔧 Setup

```bash
pip install -r requirements.txt
