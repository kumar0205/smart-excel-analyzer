import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from utils import detect_columns

def find_file(path):
    if os.path.exists(path) and os.path.isfile(path):
        return path
    
    # Check in sample_data folder
    alt_path = os.path.join("sample_data", path)
    if os.path.exists(alt_path) and os.path.isfile(alt_path):
        print(f"💡 Auto-detected in folder: {alt_path}")
        return alt_path
    
    # List available files if not found
    print(f"❌ Error: '{path}' not found.")
    print("\nSuggested files you can use:")
    extensions = (".csv", ".xlsx", ".xls")
    found_any = False
    for root, dirs, files in os.walk("."):
        if any(ignored in root for ignored in ["reports", ".git", "__pycache__"]):
            continue
        for f in files:
            if f.endswith(extensions):
                rel_path = os.path.relpath(os.path.join(root, f), ".")
                print(f" - {rel_path}")
                found_any = True
    
    if not found_any:
        print(" (No Excel or CSV files found in the project)")
    return None

file_input = input("Enter Excel/CSV path (e.g., sales_data.csv): ").strip()
file = find_file(file_input)

if not file:
    exit()

# Load file
try:
    if file.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file, engine="openpyxl")
except Exception as e:
    print(f"❌ Failed to load file: {e}")
    exit()

# Create report folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out = f"reports/report_{timestamp}"
os.makedirs(out, exist_ok=True)

print("Loaded file")

# Detect columns
mapping = detect_columns(df)
print("Detected columns:", mapping)

# Cleaning
df = df.drop_duplicates()
df = df.fillna(0)

# Convert date
if "date" in mapping:
    df[mapping["date"]] = pd.to_datetime(df[mapping["date"]], errors="coerce")

# Create total
if "price" in mapping and "quantity" in mapping:
    df["Total"] = df[mapping["price"]] * df[mapping["quantity"]]
else:
    df["Total"] = 0

df.to_csv(f"{out}/cleaned_data.csv", index=False)

# Summary
revenue = df["Total"].sum()
orders = len(df)
avg = df["Total"].mean()

summary = f"""
========================================
           BUSINESS REPORT
========================================
Report Date   : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Revenue : {revenue:,.2f}
Total Orders  : {orders}
Avg Order Val : {avg:,.2f}
----------------------------------------
"""

# Product Analysis
if "product" in mapping:
    best_product = df.groupby(mapping["product"])["Total"].sum().idxmax()
    summary += f"Best Selling Product  : {best_product}\n"

# Category Analysis
if "category" in mapping:
    best_cat = df.groupby(mapping["category"])["Total"].sum().idxmax()
    summary += f"Top Category          : {best_cat}\n"

# Customer Analysis
if "customer" in mapping:
    best_cust = df.groupby(mapping["customer"])["Total"].sum().idxmax()
    summary += f"Top Customer          : {best_cust}\n"

# Geographic Analysis
if "city" in mapping:
    best_city = df.groupby(mapping["city"])["Total"].sum().idxmax()
    summary += f"Top City              : {best_city}\n"

summary += "----------------------------------------\n"

# Growth Analysis
if "date" in mapping:
    monthly_sales = df.groupby(df[mapping["date"]].dt.to_period("M"))["Total"].sum().sort_index()
    if len(monthly_sales) > 1:
        prev_month = monthly_sales.iloc[-2]
        curr_month = monthly_sales.iloc[-1]
        growth = ((curr_month - prev_month) / prev_month) * 100 if prev_month !=0 else 0
        summary += f"Sales Growth (MoM)    : {growth:+.1f}%\n"

summary += "========================================\n"

with open(f"{out}/summary.txt","w") as f:
    f.write(summary)

print("Summary generated")

# Charts
# 1. Product Sales
if "product" in mapping:
    df.groupby(mapping["product"])["Total"].sum().sort_values(ascending=False).head(10).plot(kind="bar",title="Top 10 Products by Revenue", color="skyblue")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(f"{out}/top_products.png")
    plt.clf()

# 2. Monthly Trend
if "date" in mapping:
    monthly = df.groupby(df[mapping["date"]].dt.to_period("M"))["Total"].sum()
    monthly.index = monthly.index.astype(str)
    monthly.plot(kind="line", marker="o", title="Monthly Revenue Trend", color="green")
    plt.ylabel("Revenue")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{out}/monthly_sales.png")
    plt.clf()

# 3. Category Breakdown
if "category" in mapping:
    df.groupby(mapping["category"])["Total"].sum().plot(kind="pie", autopct="%1.1f%%", title="Revenue by Category")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"{out}/category_distribution.png")
    plt.clf()

# 4. City Performance
if "city" in mapping:
    df.groupby(mapping["city"])["Total"].sum().sort_values().plot(kind="barh", title="Revenue by City", color="salmon")
    plt.xlabel("Revenue")
    plt.tight_layout()
    plt.savefig(f"{out}/city_performance.png")
    plt.clf()

print("Charts created")

print(f"\nReport ready → {out}")
