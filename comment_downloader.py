import requests
import pandas as pd
import time
import os
import datetime
from tqdm import tqdm

# --- SETTINGS ---
API_KEY = "YOUR_API_KEY_HERE" #<-- Enter API HERE
DOCKET_ID = "DOCKET_ID" # <-- Enter Docket ID here
COMMENTS_PER_PAGE = 250
BATCH_FOLDER = f"{DOCKET_ID}_batches"
ATTACHMENT_FOLDER = os.path.join(BATCH_FOLDER, "attachments")
MASTER_CSV = os.path.join(BATCH_FOLDER, f"{DOCKET_ID}_master.csv")
BASE_URL = "https://api.regulations.gov/v4/comments"

# --- SETUP ---
os.makedirs(BATCH_FOLDER, exist_ok=True)
os.makedirs(ATTACHMENT_FOLDER, exist_ok=True)

# Load existing data
if os.path.exists(MASTER_CSV):
    existing_df = pd.read_csv(MASTER_CSV)
    existing_ids = set(existing_df["comment_id"].astype(str))
    print(f"📂 Loaded {len(existing_ids)} existing comment IDs from master.")
else:
    existing_df = pd.DataFrame()
    existing_ids = set()
    print("📁 No existing master file found. Starting fresh.")

page = 1
new_total = 0

while True:
    print(f"\n📄 Fetching page {page}...")

    params = {
        "filter[docketId]": DOCKET_ID,
        "api_key": API_KEY,
        "page[size]": COMMENTS_PER_PAGE,
        "page[number]": page
    }

    try:
        r = requests.get(BASE_URL, params=params)
    except Exception as e:
        print(f"❌ Request failed: {e}")
        break

    if r.status_code == 429:
        print("⏳ Rate limit hit. Waiting 1 hour...")
        time.sleep(3600)
        continue
    elif r.status_code != 200:
        print(f"❌ Error: {r.status_code}")
        break

    data = r.json().get("data", [])
    if not data:
        print(f"\n🏁 No more comments found from API on page {page}. Ending.")
        break

    page_results = []
    for item in data:
        cid = item["id"]
        if cid in existing_ids:
            continue  # skip duplicates

        detail_url = f"https://api.regulations.gov/v4/comments/{cid}?include=attachments&api_key={API_KEY}"
        r_detail = requests.get(detail_url)
        if r_detail.status_code != 200:
            print(f"⚠️ Failed to get details for comment {cid}")
            continue

        detail = r_detail.json()
        attr = detail.get("data", {}).get("attributes", {})
        comment_text = attr.get("comment", "").strip()
        submitter = attr.get("submitterName")
        org = attr.get("organization")
        date = attr.get("postedDate")

        pdf_path = ""
        if "See attached file" in comment_text and "included" in detail:
            for file_item in detail["included"]:
                if file_item["type"] == "attachments":
                    for file in file_item["attributes"].get("fileFormats", []):
                        if file["format"] == "pdf":
                            try:
                                file_url = file["fileUrl"]
                                file_name = f"{cid}_{file_item['id']}.pdf"
                                local_path = os.path.join(ATTACHMENT_FOLDER, file_name)
                                pdf_data = requests.get(file_url)
                                with open(local_path, "wb") as f:
                                    f.write(pdf_data.content)
                                pdf_path = local_path
                                print(f"📎 Downloaded {file_name}")
                            except Exception as e:
                                print(f"❌ Failed PDF download: {e}")
                            break

        page_results.append({
            "comment_id": cid,
            "submitted_date": date,
            "submitter": submitter,
            "organization": org,
            "comment": comment_text,
            "pdf_file_path": pdf_path
        })

        time.sleep(0.25)

    # Append page results to master
    if page_results:
        new_df = pd.DataFrame(page_results)
        existing_df = pd.concat([existing_df, new_df], ignore_index=True)
        existing_df.to_csv(MASTER_CSV, index=False)
        new_count = len(new_df)
        new_total += new_count
        existing_ids.update(new_df["comment_id"].astype(str))
        print(f"✅ Page {page} complete — {new_count} new comments added.")
    else:
        print(f"✅ Page {page} complete — 0 new comments added.")

    page += 1

print(f"\n📊 Scraping complete. {new_total} new comments added total.")
print("✅ Done.")

