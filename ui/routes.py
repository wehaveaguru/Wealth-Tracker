from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import csv
import io
import json

app = FastAPI(title="Lumina Insights API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keyword-based category mapping
CATEGORY_MAP = {
    # Shopping
    "amazon": "Shopping", "flipkart": "Shopping", "walmart": "Shopping",
    "target": "Shopping", "best buy": "Shopping", "bestbuy": "Shopping",
    "nike": "Shopping", "adidas": "Shopping", "zara": "Shopping",
    "h&m": "Shopping", "costco": "Shopping", "ikea": "Shopping",
    "ebay": "Shopping", "etsy": "Shopping", "aliexpress": "Shopping",
    "shopify": "Shopping", "macys": "Shopping", "nordstrom": "Shopping",

    # Food & Dining
    "starbucks": "Food & Dining", "mcdonalds": "Food & Dining",
    "chipotle": "Food & Dining", "subway": "Food & Dining",
    "doordash": "Food & Dining", "uber eats": "Food & Dining",
    "ubereats": "Food & Dining", "grubhub": "Food & Dining",
    "zomato": "Food & Dining", "swiggy": "Food & Dining",
    "panera": "Food & Dining", "dominos": "Food & Dining",
    "pizza hut": "Food & Dining", "kfc": "Food & Dining",
    "dunkin": "Food & Dining", "wendys": "Food & Dining",
    "taco bell": "Food & Dining", "chick-fil-a": "Food & Dining",
    "restaurant": "Food & Dining", "cafe": "Food & Dining",
    "diner": "Food & Dining", "bakery": "Food & Dining",

    # Groceries
    "whole foods": "Groceries", "trader joe": "Groceries",
    "kroger": "Groceries", "safeway": "Groceries",
    "aldi": "Groceries", "publix": "Groceries",
    "grocery": "Groceries", "supermarket": "Groceries",
    "fresh market": "Groceries", "sprouts": "Groceries",

    # Transport
    "uber": "Transport", "lyft": "Transport", "ola": "Transport",
    "shell": "Transport", "chevron": "Transport", "bp": "Transport",
    "exxon": "Transport", "gas station": "Transport",
    "parking": "Transport", "toll": "Transport",
    "metro": "Transport", "transit": "Transport",
    "fuel": "Transport", "petrol": "Transport",

    # Entertainment
    "netflix": "Entertainment", "spotify": "Entertainment",
    "disney": "Entertainment", "hulu": "Entertainment",
    "hbo": "Entertainment", "apple music": "Entertainment",
    "youtube": "Entertainment", "amc": "Entertainment",
    "cinema": "Entertainment", "theater": "Entertainment",
    "gaming": "Entertainment", "steam": "Entertainment",
    "playstation": "Entertainment", "xbox": "Entertainment",

    # Bills & Utilities
    "electric": "Bills & Utilities", "water utility": "Bills & Utilities",
    "internet": "Bills & Utilities", "phone bill": "Bills & Utilities",
    "verizon": "Bills & Utilities", "at&t": "Bills & Utilities",
    "comcast": "Bills & Utilities", "spectrum": "Bills & Utilities",
    "t-mobile": "Bills & Utilities", "insurance": "Bills & Utilities",
    "utility": "Bills & Utilities", "rent": "Bills & Utilities",
    "mortgage": "Bills & Utilities",

    # Health
    "cvs": "Health", "walgreens": "Health", "pharmacy": "Health",
    "doctor": "Health", "hospital": "Health", "clinic": "Health",
    "gym": "Health", "fitness": "Health", "dental": "Health",
    "medical": "Health", "health": "Health", "apollo": "Health",

    # Travel
    "delta": "Travel", "united": "Travel", "american airlines": "Travel",
    "southwest": "Travel", "jetblue": "Travel", "spirit": "Travel",
    "hilton": "Travel", "marriott": "Travel", "airbnb": "Travel",
    "booking.com": "Travel", "expedia": "Travel", "hotel": "Travel",
    "airline": "Travel", "flight": "Travel", "indigo": "Travel",

    # Education
    "coursera": "Education", "udemy": "Education", "udacity": "Education",
    "skillshare": "Education", "linkedin learning": "Education",
    "university": "Education", "college": "Education",
    "school": "Education", "tuition": "Education", "books": "Education",
}


def categorize_merchant(merchant_name: str) -> str:
    """Categorize a merchant by keyword matching."""
    lower = merchant_name.lower().strip()
    for keyword, category in CATEGORY_MAP.items():
        if keyword in lower:
            return category
    return "Other"


def parse_csv_content(content: str) -> list[dict]:
    """Parse CSV content into transaction records."""
    transactions = []
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    if not rows:
        return transactions

    # Try to detect header row
    first_row = rows[0]
    has_header = False
    header_lower = [col.lower().strip() for col in first_row]

    # Check if first row looks like a header
    merchant_col = None
    amount_col = None
    category_col = None

    for i, col in enumerate(header_lower):
        if col in ('merchant', 'description', 'name', 'payee', 'vendor', 'narration', 'transaction', 'details'):
            merchant_col = i
            has_header = True
        if col in ('amount', 'value', 'sum', 'debit', 'price', 'cost'):
            amount_col = i
            has_header = True
        if col in ('category', 'type', 'group', 'tag'):
            category_col = i
            has_header = True

    data_rows = rows[1:] if has_header else rows

    for row in data_rows:
        if not row or all(cell.strip() == '' for cell in row):
            continue

        try:
            if merchant_col is not None and amount_col is not None:
                # Structured CSV with known columns
                merchant = row[merchant_col].strip()
                amount_str = row[amount_col].strip().replace('$', '').replace(',', '').replace('"', '')
                amount = abs(float(amount_str))
                category = row[category_col].strip() if category_col is not None and category_col < len(row) else categorize_merchant(merchant)
            elif len(row) >= 3:
                # Try: date, merchant, amount pattern or similar
                # Find which column is numeric (amount)
                amount_found = False
                for i, cell in enumerate(row):
                    cleaned = cell.strip().replace('$', '').replace(',', '').replace('"', '').replace('-', '')
                    try:
                        amount = abs(float(cleaned))
                        if amount > 0:
                            amount_col_idx = i
                            amount_found = True
                            break
                    except ValueError:
                        continue

                if not amount_found:
                    continue

                # Merchant is the longest non-numeric, non-date text field
                merchant = ''
                for i, cell in enumerate(row):
                    if i == amount_col_idx:
                        continue
                    if len(cell.strip()) > len(merchant) and not cell.strip().replace('-', '').replace('/', '').isdigit():
                        merchant = cell.strip()

                if not merchant:
                    merchant = f"Transaction"

                category = categorize_merchant(merchant)
            elif len(row) == 2:
                # Simple: date/merchant, amount
                merchant = row[0].strip()
                amount_str = row[1].strip().replace('$', '').replace(',', '')
                amount = abs(float(amount_str))
                category = categorize_merchant(merchant)
            else:
                continue

            if amount > 0:
                transactions.append({
                    "merchant": merchant,
                    "category": category,
                    "amount": round(amount, 2)
                })
        except (ValueError, IndexError):
            continue

    return transactions


@app.post("/insights/analyze")
async def analyze_statement(file: UploadFile = File(...)):
    """
    Upload a CSV or PDF bank statement and receive categorized transactions.
    Returns: [{"merchant": "...", "category": "...", "amount": ...}, ...]
    """
    filename = file.filename.lower()

    if not (filename.endswith('.csv') or filename.endswith('.pdf')):
        raise HTTPException(status_code=400, detail="Only CSV and PDF files are supported.")

    content = await file.read()

    if filename.endswith('.csv'):
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin-1')
        transactions = parse_csv_content(text)

    elif filename.endswith('.pdf'):
        try:
            import pdfplumber
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="PDF support requires pdfplumber. Install it with: pip install pdfplumber"
            )

        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                transactions = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if not row:
                                continue
                            # Try to extract merchant and amount from table row
                            cleaned = [cell.strip() if cell else '' for cell in row]
                            amount = None
                            merchant = ''

                            for cell in cleaned:
                                val = cell.replace('$', '').replace(',', '').replace('"', '')
                                try:
                                    amount = abs(float(val))
                                except ValueError:
                                    if len(cell) > len(merchant) and not cell.replace('-', '').replace('/', '').isdigit():
                                        merchant = cell

                            if amount and amount > 0 and merchant:
                                transactions.append({
                                    "merchant": merchant,
                                    "category": categorize_merchant(merchant),
                                    "amount": round(amount, 2)
                                })
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions could be extracted from the file.")

    return transactions


@app.get("/health")
def health_check():
    return {"status": "ok"}
