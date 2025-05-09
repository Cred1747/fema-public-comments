import requests
import pandas as pd
import time
import os
import datetime
from tqdm import tqdm

# --- SETTINGS ---
API_KEY = "YOUR_API_KEY_HERE"
DOCKET_ID = "DHS-2025-0013"
COMMENTS_PER_PAGE = 250
PAGES_PER_HOUR = 3
BATCH_FOLDER = f"{DOCKET_ID}_batches"
ATTACHMENT_FOLDER = os.path.join(BATCH_FOLDER, "attachments")
MASTER_CSV = os.path.join(BATCH_FOLDER, f"{DOCKET_ID}_master.csv")
BASE_URL = "https://api.regulations.gov/v4/comments"

# --- SETUP ---
os.makedirs(BATCH_FOLDER, exist_ok=True)
os.makedirs(ATTACHMENT_FOLDER, exist_ok=True)

start_page = 1
batch_number = 1

# Load existing master file if it exists
if os.path.exists(MASTER_CSV):
    existing_df = pd.read_csv(MASTER_CSV)
    existing_ids = set(existing_df["comment_id"].astype(str))
    print(f"📂 Loaded {len(existing_ids)} existing comment IDs from master.")
else:
    existing_df = pd.DataFrame()
    existing_ids = set()

# --- Main loop ---
while True:
    hour_start = datetime.datetime.now()
    batch_results = []
    pages = range(start_page, start_page + PAGES_PER_HOUR)

    print(f"\n⏳ Starting Batch #{batch_number} at {hour_start.strftime('%H:%M:%S')} (Pages: {list(pages)})")

    for page in tqdm(pages, desc=f"📄 Batch {batch_number} - Pages"):
        params = {
            "filter[docketId]": DOCKET_ID,
            "api_key": API_KEY,
            "page[size]": COMMENTS_PER_PAGE,
            "page[number]": page
        }

        r = requests.get(BASE_URL, params=params)
        if r.status_code != 200:
            print(f"❌ Error fetching page {page}: {r.status_code}")
            continue

        ids = [item["id"] for item in r.json().get("data", [])]
        if not ids:
            print("✅ No more data available.")
            break

        for cid in ids:
            if cid in existing_ids:
                continue

            print(f"🔍 Processing comment {cid}")
            detail_url = f"https://api.regulations.gov/v4/comments/{cid}?include=attachments&api_key={API_KEY}"
            r_detail = requests.get(detail_url)
            if r_detail.status_code != 200:
                print(f"⚠️ Failed to get details for comment {cid}")
                continue

            data = r_detail.json()
            attr = data.get("data", {}).get("attributes", {})
            comment_text = attr.get("comment", "").strip()
            submitter = attr.get("submitterName")
            org = attr.get("organization")
            date = attr.get("postedDate")

            pdf_path = ""
            if "See attached file" in comment_text and "included" in data:
                for item in data["included"]:
                    if item["type"] == "attachments":
                        for file in item["attributes"].get("fileFormats", []):
                            if file["format"] == "pdf":
                                file_url = file["fileUrl"]
                                file_name = f"{cid}_{item['id']}.pdf"
                                local_path = os.path.join(ATTACHMENT_FOLDER, file_name)
                                try:
                                    pdf_data = requests.get(file_url)
                                    with open(local_path, "wb") as f:
                                        f.write(pdf_data.content)
                                    pdf_path = local_path
                                    print(f"📎 Downloaded {file_name}")
                                except Exception as e:
                                    print(f"❌ Failed to download PDF {file_url}: {e}")
                                break

            batch_results.append({
                "comment_id": cid,
                "submitted_date": date,
                "submitter": submitter,
                "organization": org,
                "comment": comment_text,
                "pdf_file_path": pdf_path
            })

            time.sleep(0.2)

    # Save new comments to master
    if batch_results:
        new_df = pd.DataFrame(batch_results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(MASTER_CSV, index=False)
        print(f"💾 Updated master CSV with {len(new_df)} new comments. Total: {len(combined_df)}")

        existing_df = combined_df
        existing_ids.update(new_df["comment_id"].astype(str))
    else:
        print("📭 No new comments found in this batch.")

    batch_number += 1
    start_page += PAGES_PER_HOUR

    if len(batch_results) < COMMENTS_PER_PAGE * PAGES_PER_HOUR:
        print("🏁 Final batch smaller than full size — ending.")
        break

    elapsed = (datetime.datetime.now() - hour_start).seconds
    wait_time = max(0, 3600 - elapsed)
    print(f"🕒 Waiting {wait_time} seconds before next batch...")

    with tqdm(total=wait_time, desc="⏱️ Cooldown", bar_format="{l_bar}{bar} | ETA: {remaining} sec") as t:
        for _ in range(wait_time):
            time.sleep(1)
            t.update(1)
