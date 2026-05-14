import pandas as pd
from urllib.parse import urlparse

INPUT_FILE = ".csv" # YOUR FILE HERE
OUTPUT_FILE = ".csv" # file to save to, e.g. "shopify_redirects.csv"

df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")

def clean(x):
    return str(x).strip()

redirects = {}

for _, row in df.iterrows():
    parent_url = clean(row.get("Parent Product Url", ""))
    if not parent_url:
        continue

    # Make sure urlparse gets a full URL
    if not parent_url.startswith("http"):
        full_url = "https://www.westwoodsfootwear.co.uk" + parent_url
    else:
        full_url = parent_url

    path = urlparse(full_url).path.strip("/")
    if not path:
        continue

    handle = path.split("/")[-1]
    old_path = "/" + path
    new_path = f"/products/{handle}"

    redirects[old_path] = new_path  # de-dupes automatically

out = pd.DataFrame(
    [{"Redirect from": old, "Redirect to": new} for old, new in redirects.items()]
)

out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"Done. Saved to {OUTPUT_FILE}")