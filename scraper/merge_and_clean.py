"""
merge_and_clean.py — Merge All 5 Platform CSVs & Clean Pipeline
================================================================
Steps:
  1. Run all 5 scrapers to generate platform CSVs
  2. Load all 5 CSVs
  3. Merge into one DataFrame
  4. Full cleaning pipeline:
     - Deduplicate
     - Normalize cities
     - Standardize skills
     - Parse experience
     - Normalize salary
     - Classify missing domains
     - Remove invalids
  5. Save final_merged_jobs.csv

Run:
    python scrapers/merge_and_clean.py
"""

import os, sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_data import (
    COLUMNS, normalize_city, standardize_skills,
    parse_experience, normalize_salary, classify_domain,
    deduplicate,
)

# Import scrapers
from naukri_scraper    import run as run_naukri
from linkedin_scraper  import run as run_linkedin
from other_scrapers    import (
    run_indeed       as run_indeed,
    run_glassdoor    as run_glassdoor,
    run_internshala  as run_internshala,
)

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")
FINAL_CSV  = os.path.join(DATA_DIR, "final_merged_jobs.csv")
os.makedirs(DATA_DIR, exist_ok=True)

PLATFORM_CSVS = {
    "Naukri"     : os.path.join(DATA_DIR, "naukri_jobs.csv"),
    "LinkedIn"   : os.path.join(DATA_DIR, "linkedin_jobs.csv"),
    "Indeed"     : os.path.join(DATA_DIR, "indeed_jobs.csv"),
    "Glassdoor"  : os.path.join(DATA_DIR, "glassdoor_jobs.csv"),
    "Internshala": os.path.join(DATA_DIR, "internshala_jobs.csv"),
}


# ─────────────────────────────────────────────────────────────
# STEP 1 — RUN ALL SCRAPERS
# ─────────────────────────────────────────────────────────────
def run_all_scrapers():
    """Generate all 5 platform CSV files."""
    print("\n" + "=" * 60)
    print("  STEP 1 — RUNNING ALL 5 PLATFORM SCRAPERS")
    print("=" * 60)

    run_naukri(use_live=False,       n_per_city=375)
    print()
    run_linkedin(use_live=False,     n_per_city=300)
    print()
    run_indeed(use_live=False,       n_per_city=325)
    print()
    run_glassdoor(use_live=False,    n_per_city=300)
    print()
    run_internshala(use_live=False,  n_per_city=500)

    print("\n  ✅ All 5 scrapers completed!")


# ─────────────────────────────────────────────────────────────
# STEP 2 — LOAD & MERGE ALL CSVs
# ─────────────────────────────────────────────────────────────
def load_and_merge() -> pd.DataFrame:
    """Load all platform CSVs and merge into one DataFrame."""
    print("\n" + "=" * 60)
    print("  STEP 2 — LOADING & MERGING ALL PLATFORM CSVs")
    print("=" * 60)

    dfs = []
    for platform, path in PLATFORM_CSVS.items():
        if os.path.exists(path):
            df = pd.read_csv(path, encoding="utf-8-sig")
            print(f"  {platform:<15} : {len(df):>5} records loaded from {os.path.basename(path)}")
            dfs.append(df)
        else:
            print(f"  {platform:<15} : ⚠️  File not found — {path}")

    if not dfs:
        raise FileNotFoundError("No platform CSV files found! Run scrapers first.")

    merged = pd.concat(dfs, ignore_index=True)
    print(f"\n  Combined total   : {len(merged):,} records")
    return merged


# ─────────────────────────────────────────────────────────────
# STEP 3 — FULL CLEANING PIPELINE
# ─────────────────────────────────────────────────────────────
def clean_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete data cleaning pipeline:
    1.  Ensure all columns exist
    2.  Remove exact duplicate rows
    3.  Normalize city names
    4.  Standardize skill names
    5.  Parse experience to numeric
    6.  Normalize salary to annual INR
    7.  Classify missing/empty domains
    8.  Drop records with no title or company
    9.  Strip whitespace from all string columns
    10. Remove records with unknown cities
    11. Content-fingerprint deduplication
    12. Reset index
    """
    print("\n" + "=" * 60)
    print("  STEP 3 — DATA CLEANING PIPELINE")
    print("=" * 60)
    print(f"  Input records : {len(df):,}")

    # 1. Ensure all expected columns exist
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS].copy()

    # 2. Exact duplicate removal
    before = len(df)
    df = df.drop_duplicates()
    print(f"  [step 2] Exact dupes removed  : {before - len(df):>5}")

    # 3. Normalize city names
    df["city"] = df["city"].apply(normalize_city)
    print(f"  [step 3] Cities normalized     : {df['city'].value_counts().to_dict()}")

    # 4. Standardize skill names
    df["skills"] = df["skills"].apply(standardize_skills)

    # 5. Parse experience → numeric
    df["experience_years"] = df["experience"].apply(parse_experience)

    # 6. Normalize salary → annual INR
    # Only recalculate where salary_annual_inr is missing/0
    mask_sal = df["salary_annual_inr"].isna() | (df["salary_annual_inr"] == 0)
    df.loc[mask_sal, "salary_annual_inr"] = df.loc[mask_sal, "salary"].apply(normalize_salary)
    print(f"  [step 6] Salary parsed         : {(~df['salary_annual_inr'].isna()).sum()} records with salary")

    # 7. Classify missing/empty domains
    mask_dom = df["job_domain"].isna() | (df["job_domain"].str.strip() == "")
    if mask_dom.any():
        df.loc[mask_dom, "job_domain"] = df[mask_dom].apply(
            lambda r: classify_domain(r["job_title"], r["skills"]), axis=1
        )
        print(f"  [step 7] Domains classified    : {mask_dom.sum()} records re-classified")

    # 8. Drop records with no title or company
    before = len(df)
    df = df.dropna(subset=["job_title", "company_name"])
    df = df[df["job_title"].str.strip() != ""]
    df = df[df["company_name"].str.strip() != ""]
    print(f"  [step 8] Empty title/company   : {before - len(df):>5} removed")

    # 9. Strip whitespace from all string columns
    str_cols = ["job_title", "company_name", "location", "city",
                "experience", "salary", "skills", "job_type",
                "source_portal", "job_domain"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 10. Remove records with unknown/invalid cities
    valid_cities = ["Surat", "Ahmedabad", "Vadodara", "Gandhinagar"]
    before = len(df)
    df = df[df["city"].isin(valid_cities)]
    print(f"  [step 10] Invalid cities       : {before - len(df):>5} removed")

    # 11. Content-fingerprint deduplication
    print("  [step 11] Fingerprint dedup    :", end=" ")
    df = deduplicate(df)

    # 12. Reset index
    df = df.reset_index(drop=True)
    df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")

    print(f"\n  Output records : {len(df):,}")
    return df


# ─────────────────────────────────────────────────────────────
# STEP 4 — SUMMARY REPORT
# ─────────────────────────────────────────────────────────────
def print_summary(df: pd.DataFrame):
    """Print detailed summary of merged cleaned dataset."""
    print("\n" + "=" * 60)
    print("  MERGED DATASET SUMMARY")
    print("=" * 60)

    print(f"""
  Total Records    : {len(df):,}
  Unique Companies : {df['company_name'].nunique():,}
  Unique Job Titles: {df['job_title'].nunique():,}
  IT Domains       : {df['job_domain'].nunique()}
  Portals          : {df['source_portal'].nunique()}
  Date Range       : {df['date_posted'].min().date()} → {df['date_posted'].max().date()}
""")

    print("  RECORDS PER PORTAL:")
    print("  " + "-" * 40)
    for portal, cnt in df["source_portal"].value_counts().items():
        bar = "█" * int(cnt / 30)
        pct = cnt / len(df) * 100
        print(f"  {portal:<15} {cnt:>5} ({pct:>4.1f}%)  {bar}")

    print("\n  RECORDS PER CITY:")
    print("  " + "-" * 40)
    for city, cnt in df["city"].value_counts().items():
        pct = cnt / len(df) * 100
        bar = "█" * int(cnt / 30)
        print(f"  {city:<15} {cnt:>5} ({pct:>4.1f}%)  {bar}")

    print("\n  TOP 10 DOMAINS:")
    print("  " + "-" * 40)
    for dom, cnt in df["job_domain"].value_counts().head(10).items():
        print(f"  {dom[:38]:<38} {cnt:>5}")

    print("\n  JOB TYPES:")
    print("  " + "-" * 40)
    for jt, cnt in df["job_type"].value_counts().items():
        pct = cnt / len(df) * 100
        print(f"  {jt:<15} {cnt:>5} ({pct:>4.1f}%)")

    sal_df = df[df["salary_annual_inr"] > 0].copy()
    sal_df["lpa"] = sal_df["salary_annual_inr"] / 100_000
    print(f"\n  SALARY STATS (where disclosed):")
    print(f"  Records with salary: {len(sal_df):,}")
    print(f"  Min salary         : ₹{sal_df['lpa'].min():.1f} LPA")
    print(f"  Max salary         : ₹{sal_df['lpa'].max():.1f} LPA")
    print(f"  Avg salary         : ₹{sal_df['lpa'].mean():.1f} LPA")
    print(f"  Median salary      : ₹{sal_df['lpa'].median():.1f} LPA")
    print("=" * 60)


# ─────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────────────────────
def run_full_pipeline(skip_scraping: bool = False):
    """
    Full pipeline:
    1. Run all 5 scrapers
    2. Load & merge CSVs
    3. Clean data
    4. Save final CSV
    5. Print summary
    """
    print("\n" + "═" * 60)
    print("  IT JOB MARKET — FULL DATA PIPELINE")
    print("  Gujarat, India | 5 Platforms")
    print("═" * 60)

    # Step 1 — Scrape
    if not skip_scraping:
        run_all_scrapers()

    # Step 2 — Merge
    merged_raw = load_and_merge()

    # Step 3 — Clean
    clean_df = clean_pipeline(merged_raw)

    # Step 4 — Save
    clean_df.to_csv(FINAL_CSV, index=False, encoding="utf-8-sig")
    print(f"\n  [saved] {FINAL_CSV}")

    # Step 5 — Summary
    print_summary(clean_df)

    print("\n  ✅ Full pipeline complete!")
    print(f"  Upload '{os.path.basename(FINAL_CSV)}' to Colab for analytics.")
    print("═" * 60)

    return clean_df


if __name__ == "__main__":
    run_full_pipeline(skip_scraping=False)
