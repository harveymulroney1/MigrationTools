# Visualsoft to Shopify Migration Tools

Unofficial Python tools for converting Visualsoft-style product export CSVs into Shopify-compatible CSV files.

This project was created to support an e-commerce migration from Visualsoft to Shopify. It focuses on transforming product data, variant data, product image URLs, Google Shopping fields, and product redirects into formats that are easier to review and import into Shopify.

## Disclaimer

This project is not affiliated with, endorsed by, sponsored by, or maintained by Visualsoft or Shopify.

No Visualsoft source code, proprietary platform code, private documentation, customer data, or real store export data is included in this repository.

The scripts are designed to work with CSV exports that follow a Visualsoft-style structure, but they may need adjusting depending on the exact export format.

## What this project does

This repository currently includes tools for:

- Converting product export data into Shopify product import rows
- Creating Shopify handles from product URLs or product references
- Mapping parent/child products into Shopify product and variant rows
- Cleaning prices, stock values, tags, titles, and image URLs
- Assigning Shopify product status based on active/inactive source fields
- Adding basic Google Shopping fields such as gender, age group, condition, and custom product
- Creating Shopify product redirects from old Visualsoft product URLs
- De-duplicating redirects automatically

## Project structure

```txt
├── productConverter.py
├── redirectCreatorProducts.py
├── .env.example
├── .gitignore
└── README.md
