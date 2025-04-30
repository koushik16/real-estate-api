import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv

def clean_and_load_csv(path):
    fixed_rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0].lower().startswith("median price") and len(row) > 4:
                new_row = [row[0], row[1], row[2]+row[3], row[4]+row[5]]
                fixed_rows.append(new_row)
            else:
                fixed_rows.append(row)
    df = pd.DataFrame(fixed_rows[1:], columns=fixed_rows[0])
    df.set_index("Metric", inplace=True)
    df = df.replace(r"[$,]", "", regex=True).apply(pd.to_numeric, errors="coerce")
    return df
def generate_market_plot(region: str, subject: dict, comparables: list, output_path: str):
    folder_path = f"app/data/{region}"
    data_frames = []

    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".csv"):
            date = filename.replace(".csv", "")
            df = clean_and_load_csv(os.path.join(folder_path, filename))
            if "Median Price" in df.index:
                median_row = df.loc["Median Price"].to_frame().T
                median_row["Date"] = date
                data_frames.append(median_row)

    combined_df = pd.concat(data_frames).set_index("Date").sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    ptype = subject["type"]
    ax.plot(combined_df.index, combined_df[ptype], label=f"{ptype} Market Trend", linewidth=2, marker='o', color='steelblue')

    subject_price = combined_df.loc[subject["effective_date"], ptype]
    ax.scatter(subject["effective_date"], subject_price, color='green', s=100, label="Subject")
    ax.text(subject["effective_date"], subject_price + 5000, "Subject", ha='center', color='green')

    for idx, comp in enumerate(comparables):
        ctype, cdate, cprice = subject["type"], comp["date"], comp["price"]
        if cdate in combined_df.index:
            pct_diff = ((cprice - subject_price) / subject_price) * 100
            label = f"{comp.get('label', f'Comp {idx+1}')} ({pct_diff:+.1f}%)"
            ax.scatter(cdate, cprice, color='orange', s=80)
            ax.text(cdate, cprice - 7000, label, ha='center', fontsize=9)
            ax.plot([cdate, subject["effective_date"]], [cprice, subject_price], linestyle='dotted', color='gray')

            csv_file = os.path.join(folder_path, f"{cdate}.csv")
            if os.path.exists(csv_file):
                full_df = clean_and_load_csv(csv_file)
                if ctype in full_df.columns:
                    median = full_df.loc["Median Price", ctype]
                    avg_days = int(full_df.loc["Average selling time (Days)", ctype])
                    sales = int(full_df.loc["Sales", ctype])
                    listings = int(full_df.loc["Active Listings", ctype])
                    listings_str = f"{listings/1000:.1f}k" if listings >= 1000 else str(listings)
                    box_text = f"{label}\nSale Price: ${cprice:,.0f}\nMedian: ${median:,.0f}\nSales: {sales}\nListings: {listings_str}\nAvg Days: {avg_days}"
                    ax.text(1.02, 0.95 - idx * 0.2, box_text,
                            transform=ax.transAxes,
                            fontsize=9,
                            verticalalignment='top',
                            bbox=dict(boxstyle="round,pad=0.4", facecolor='whitesmoke', edgecolor='gray'))

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title(f"Market Condition Adjustment – {region.replace('_', ' ')}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (CAD)")
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()
