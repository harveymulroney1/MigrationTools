import pandas as pd
import re
from urllib.parse import urlparse

web_url = "https://www.YOURSTORE.co.uk"

INPUT_FILE = "input.csv" # input file
OUTPUT_FILE = "output.csv" # output file

# Read everything as text so Excel formatting doesn't break fields
df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")

def clean(value):
    return str(value).strip()

def parse_bool(value):
    value = clean(value).lower()
    return value in {"y", "yes", "true", "1"}

def make_handle(parent_url, parent_ref, parent_id):
    parent_url = clean(parent_url)
    parent_ref = clean(parent_ref)
    parent_id = clean(parent_id)

    if parent_url:
        if not parent_url.startswith("http"):
            parent_url = web_url + parent_url
        path = urlparse(parent_url).path.strip("/")
        if path:
            return path.split("/")[-1].lower()

    if parent_ref:
        handle = re.sub(r"[^a-z0-9]+", "-", parent_ref.lower()).strip("-")
        handle = re.sub(r"-+", "-", handle)
        if handle:
            return handle

    return f"product-{parent_id}"

# Testing Building Title
def build_title(brand, raw_title):
    brand = clean(brand)
    raw_title = clean(raw_title)

    if not raw_title:
        return brand

    if not brand:
        return raw_title

    # Don't duplicate brand name if already at start
    if raw_title.lower().startswith(brand.lower() + " "):
        return raw_title

    # Also avoid cases like "Rieker-25051..." or exact brand-only titles
    normalised_title = re.sub(r"[\s\-_:]+", " ", raw_title.lower()).strip()
    normalised_brand = re.sub(r"[\s\-_:]+", " ", brand.lower()).strip()

    if normalised_title == normalised_brand:
        return raw_title

    if normalised_title.startswith(normalised_brand + " "):
        return raw_title

    return f"{brand} {raw_title}"
# for meta fields - converts to this format:
def map_category(cat):
    if "slipper" in cat.lower():
        return "Apparel & Accessories > Shoes > Slippers"
    if "sandal" in cat.lower():
        return "Apparel & Accessories > Shoes > Sandals"
    if "boot" in cat.lower():
        return "Apparel & Accessories > Shoes > Boots"
    
def map_google_fields(raw_category, title):
    text = f"{raw_category} {title}".lower()

    if "mens" in text or "men's" in text:
        gender = "male"
    elif "womens" in text or "women's" in text or "ladies" in text:
        gender = "female"
    else:
        gender = "unisex"

    return {
        "Google Shopping / Gender": gender,
        "Google Shopping / Age Group": "adult",
        "Google Shopping / Condition": "new",
        "Google Shopping / Custom Product": "FALSE"
    }
def split_images(raw):
    raw = str(raw).replace('"', "").strip()
    if not raw:
        return []
    return [line.strip() for line in raw.splitlines() if line.strip()]

def build_tags(row):
    raw_parts = [
        row.get("Categories", ""),
        row.get("Tag 10 (Gender)", ""),
        row.get("Tag 11 (Boot Style)", ""),
        row.get("Tag 8 (Colour)", ""),
        row.get("Brand", "")
    ]

    tags = []
    for part in raw_parts:
        part = clean(part)
        if not part:
            continue
        for t in re.split(r",|>", part):
            t = t.strip()
            if t:
                tags.append(t)

    seen = set()
    deduped = []
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(tag)

    return ", ".join(deduped)

def normalise_price(value):
    return clean(value).replace("£", "").replace(",", "")

def normalise_stock(value):
    value = clean(value).replace(",", "")
    if value == "":
        return ""
    try:
        return str(int(float(value)))
    except Exception:
        return value

shopify_rows = []
added_image_sets = set()

for _, row in df.iterrows():
    parent_id = clean(row.get("VS Parent ID", ""))
    child_id = clean(row.get("VS Child ID", ""))
    parent_ref = clean(row.get("Parent Reference", ""))
    child_ref = clean(row.get("Child Reference", ""))
    raw_title = clean(row.get("Parent Product Title", "")) or clean(row.get("Child Product Title", ""))
    vendor = clean(row.get("Brand", ""))
    title = build_title(vendor, raw_title)
    body_html = clean(row.get("Product Description", ""))
    vendor = clean(row.get("Brand", ""))
    colour = clean(row.get("Attribute 1 (Colour)", ""))
    size = clean(row.get("Attribute 2 (Size)", ""))
    barcode = clean(row.get("EAN", ""))
    price = normalise_price(row.get("Price (Inc VAT)", ""))
    sale_price = normalise_price(row.get("Sale Price (Inc VAT)", ""))
    rrp_price = normalise_price(row.get("RRP Price (Inc VAT)", ""))
    cost_price = normalise_price(row.get("Cost Price (Inc VAT)", ""))
    stock_qty = normalise_stock(row.get("Stock Value", ""))
    parent_url = clean(row.get("Parent Product Url", ""))
    meta_title = clean(row.get("Meta Title", ""))
    meta_description = clean(row.get("Meta Description", ""))

    parent_active = parse_bool(row.get("Parent Active", ""))
    child_active = parse_bool(row.get("Child Active", ""))

    # Google Requirements
    shopify_category = map_category(row["Category"])
    google_fields = map_google_fields(row["Category"], row["Title"])

    published = "TRUE" if (parent_active and child_active) else "FALSE"
    status = "active" if (parent_active and child_active) else "draft"

    handle = make_handle(parent_url, parent_ref, parent_id)

    child_images = split_images(row.get("Child Product Images", ""))
    parent_images = split_images(row.get("Parent Product Images", ""))
    images = child_images if child_images else parent_images

    sku = child_ref if child_ref else child_id

    compare_at_price = ""
    if rrp_price and rrp_price != price:
        compare_at_price = rrp_price
    elif sale_price and price and sale_price != price:
        compare_at_price = price
        price = sale_price

    base_row = {
        "Handle": handle,
        "Title": title,
        "Body (HTML)": body_html,
        "Vendor": vendor,
        "Type": clean(row.get("Categories", "")),
        "Tags": build_tags(row),
        "Published": published,

        "Product Category": shopify_category,
        "Google Shopping / Gender": google_fields["Google Shopping / Gender"],
        "Google Shopping / Age Group": google_fields["Google Shopping / Age Group"],
        "Google Shopping / Condition": google_fields["Google Shopping / Condition"],
        "Google Shopping / Custom Product": google_fields["Google Shopping / Custom Product"],

        "Option1 Name": "Colour" if colour else "",
        "Option1 Value": colour,
        "Option2 Name": "Size" if size else "",
        "Option2 Value": size,

        "Variant SKU": sku,
        "Variant Inventory Tracker": "shopify",
        "Variant Inventory Qty": stock_qty,
        "Variant Inventory Policy": "deny",
        "Variant Fulfillment Service": "manual",
        "Variant Price": price,
        "Variant Compare At Price": compare_at_price,
        "Variant Requires Shipping": "TRUE",
        "Variant Taxable": "TRUE",
        "Variant Barcode": barcode,

        "Image Src": images[0] if images else "",
        "Image Position": "1" if images else "",
        "Variant Image": images[0] if images else "",

        "SEO Title": meta_title,
        "SEO Description": meta_description,
        "Cost per item": cost_price,
        "Status": status,
    }

    shopify_rows.append(base_row)

    image_group_key = (handle, colour.lower() if colour else "no-colour")

    if images and image_group_key not in added_image_sets:
        for i, image_url in enumerate(images[1:], start=2):
            image_row = {
                "Handle": handle,
                "Image Src": image_url,
                "Image Position": str(i),
            }
            shopify_rows.append(image_row)

        added_image_sets.add(image_group_key)

out_df = pd.DataFrame(shopify_rows)
out_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Done. File Saved to {OUTPUT_FILE}")