
import requests
import pandas as pd
import os
import time

# SETTINGS
API_KEY = "YOUR_API_KEY"  # Replace with your real API key
DOCKET_ID = "DHS-2025-0013"
OUTPUT_CSV = f"{DOCKET_ID}_all_comments.csv"
ATTACHMENT_FOLDER = "attachments"
os.makedirs(ATTACHMENT_FOLDER, exist_ok=True)

# --- Collect all comment IDs ---
def get_comment_ids(docket_id):
    comment_ids = []
    url = "https://api.regulations.gov/v4/comments"
    params = {
        "filter[docketId]": docket_id,
        "api_key": API_KEY,
        "page[size]": 250
    }

    print("🔍 Collecting all comment IDs...")
    while url:
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print("❌ Failed to fetch page:", r.text)
            break
        data = r.json()
        ids_in_page = [item["id"] for item in data.get("data", [])]
        comment_ids.extend(ids_in_page)
        print(f"📥 Fetched {len(ids_in_page)} IDs (total so far: {len(comment_ids)})")
        url = data.get("links", {}).get("next")
        params = {}  # next link includes query
    return comment_ids

# --- Download attachments (PDF only) ---
def download_pdf(comment_id, attachment_data):
    for file in attachment_data.get("attributes", {}).get("fileFormats", []):
        if file["format"] == "pdf":
            file_url = file["fileUrl"]
            file_name = f"{comment_id}_{attachment_data['id']}.pdf"
            local_path = os.path.join(ATTACHMENT_FOLDER, file_name)
            try:
                r = requests.get(file_url)
                with open(local_path, "wb") as f:
                    f.write(r.content)
                print(f"📎 Downloaded {file_name}")
                return local_path
            except Exception as e:
                print(f"❌ Failed to download {file_url}: {e}")
    return ""

# --- Fetch full comment details ---
def fetch_comments(comment_ids):
    results = []
    for i, cid in enumerate(comment_ids):
        url = f"https://api.regulations.gov/v4/comments/{cid}?include=attachments&api_key={API_KEY}"
        r = requests.get(url)
        if r.status_code != 200:
            print(f"❌ Failed to fetch: {cid}")
            continue

        data = r.json()
        attr = data.get("data", {}).get("attributes", {})
        comment_text = attr.get("comment", "").strip()
        pdf_path = ""

        if "See attached file" in comment_text and "included" in data:
            for inc in data["included"]:
                if inc["type"] == "attachments":
                    pdf_path = download_pdf(cid, inc)
                    break

        results.append({
            "comment_id": cid,
            "submitted_date": attr.get("postedDate"),
            "submitter": attr.get("submitterName"),
            "organization": attr.get("organization"),
            "comment": comment_text,
            "pdf_file_path": pdf_path
        })

        if (i + 1) % 25 == 0:
            print(f"🔄 Processed {i + 1}/{len(comment_ids)}")
        time.sleep(0.1)
    return results

# --- Run everything ---
ids = get_comment_ids(DOCKET_ID)
print(f"✅ Collected {len(ids)} IDs. Fetching comment details...")
data = fetch_comments(ids)
df = pd.DataFrame(data)
df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Done! {len(df)} records saved to {OUTPUT_CSV}")
