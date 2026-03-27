"""
glassdoor_scraper.py — Glassdoor Job Data Collector
====================================================
Platform Profile:
  - Reviews + Jobs platform
  - Salary transparency (many disclosed)
  - Mid to Senior level dominant
  - Enterprise & MNC companies
  - Company ratings visible

Live Scraping Method:
  - Selenium WebDriver (login required for full data)
  - Handles JS-rendered content
  - Pagination via page parameter in URL

Simulated Data Profile:
  - Higher salary disclosure rate
  - Skews mid-senior (no freshers)
  - Strong enterprise domain coverage
  - Company names include ratings (★)

Output: data/glassdoor_jobs.csv (~1,102 records)

Run:
    python scrapers/glassdoor_scraper.py
"""

import os, sys, time, random
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_data import (
    COLUMNS, CITIES, GLASSDOOR_COMPANIES, DOMAIN_TECH,
    DOMAIN_TITLES, CITY_DOMAIN_WEIGHTS, build_record,
    deduplicate, random_date, classify_domain,
)

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "glassdoor_jobs.csv"
)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


# ─────────────────────────────────────────────────────────────
# LIVE SCRAPER — Glassdoor (Selenium WebDriver)
# ─────────────────────────────────────────────────────────────
def live_scrape(city: str, keyword: str, pages: int = 5) -> list:
    """
    Scrape Glassdoor job listings using Selenium.

    Note: Glassdoor requires login for full salary/review data.
    This scraper extracts publicly visible job listings.

    URL pattern:
        glassdoor.co.in/Jobs/{city}-{keyword}-jobs-SRCH_...htm

    Args:
        city    : Target city
        keyword : Job search keyword
        pages   : Number of pages to scrape

    Returns:
        list of job record dicts
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("  [glassdoor] selenium not installed — using simulator")
        return []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    jobs   = []

    try:
        for page in range(1, pages + 1):
            url = (
                f"https://www.glassdoor.co.in/Jobs/"
                f"{city.lower()}-{keyword.replace(' ', '-').lower()}-jobs"
                f"-SRCH_IL.0,{len(city)}_IC{page}.htm"
            )
            print(f"    [glassdoor-live] Page {page}: {url}")
            driver.get(url)
            time.sleep(3)

            # Scroll to load lazy content
            for _ in range(4):
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(1.5)

            # Job listing cards
            cards = driver.find_elements(
                By.XPATH,
                "//li[contains(@class,'react-job-listing')]"
            )

            for card in cards:
                try:
                    title   = card.find_element(
                        By.XPATH, ".//a[contains(@class,'job-title')]"
                    ).text.strip()
                    company = card.find_element(
                        By.XPATH, ".//span[contains(@class,'employer-name')]"
                    ).text.strip()
                    loc     = card.find_element(
                        By.XPATH, ".//span[contains(@class,'location')]"
                    ).text.strip()
                    sal_els = card.find_elements(
                        By.XPATH, ".//span[contains(@class,'salary')]"
                    )
                    salary  = sal_els[0].text.strip() if sal_els else "Not Disclosed"

                    if title and company:
                        jobs.append({
                            "job_title"        : title,
                            "company_name"     : company,
                            "location"         : loc,
                            "city"             : city,
                            "experience"       : "",
                            "salary"           : salary,
                            "skills"           : "",
                            "job_description"  : "",
                            "job_domain"       : classify_domain(title, ""),
                            "job_type"         : "Full-time",
                            "date_posted"      : random_date(30),
                            "source_portal"    : "Glassdoor",
                            "experience_years" : 0.0,
                            "salary_annual_inr": float("nan"),
                        })
                except Exception:
                    continue

            time.sleep(random.uniform(3.0, 5.0))

    finally:
        driver.quit()

    print(f"    [glassdoor-live] Collected {len(jobs)} jobs from {city}")
    return jobs


# ─────────────────────────────────────────────────────────────
# SIMULATOR — Glassdoor-style realistic data
# ─────────────────────────────────────────────────────────────
def simulate_glassdoor(n_per_city: int = 300, seed: int = 404) -> list:
    """
    Generate realistic Glassdoor-style job listings.

    Glassdoor Profile:
      - Company-branded listings (ratings visible)
      - Higher salary transparency
      - Skews mid-senior level
      - Strong in enterprise / MNC companies
      - Many verified employer listings

    Args:
        n_per_city : Records per city (default 300 → 1,200 total)
        seed       : Random seed

    Returns:
        list of job record dicts
    """
    random.seed(seed)
    np.random.seed(seed)

    # Glassdoor skews mid-senior
    LEVEL_DIST = [
        ("fresher",   0.08),
        ("junior",    0.18),
        ("mid",       0.32),
        ("senior",    0.28),
        ("lead",      0.10),
        ("principal", 0.04),
    ]
    levels_pool   = [l for l, w in LEVEL_DIST
                     for _ in range(int(w * 100))]
    JOB_TYPE_DIST = (
        ["Full-time"] * 80 +
        ["Contract"]  * 15 +
        ["Part-time"] * 5
    )

    all_records = []

    for city in CITIES:
        companies  = GLASSDOOR_COMPANIES[city]
        weights    = CITY_DOMAIN_WEIGHTS[city]
        domains    = list(weights.keys())
        dom_probs  = [weights[d] for d in domains]

        for _ in range(n_per_city):
            domain   = random.choices(domains, weights=dom_probs)[0]
            title    = random.choice(DOMAIN_TITLES[domain])
            tech     = random.choice(DOMAIN_TECH[domain])
            company  = random.choice(companies)
            level    = random.choice(levels_pool)
            job_type = random.choice(JOB_TYPE_DIST)

            record   = build_record(
                job_title = title,
                company   = company,
                city      = city,
                domain    = domain,
                tech      = tech,
                level     = level,
                job_type  = job_type,
                portal    = "Glassdoor",
                days_back = 60,
                is_intern = False,
            )
            all_records.append(record)

    print(f"  [glassdoor-sim] Generated {len(all_records)} records")
    return all_records


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def run(use_live: bool = False, n_per_city: int = 300):
    """
    Run Glassdoor data collection pipeline.

    Args:
        use_live   : If True attempts live scraping first
        n_per_city : Records per city in simulation
    """
    print("=" * 55)
    print("  GLASSDOOR SCRAPER")
    print("=" * 55)

    records = []

    if use_live:
        keywords = [
            "Software Engineer", "Data Analyst",
            "DevOps Engineer", "Cloud Engineer",
            "Cybersecurity Analyst", "Product Manager",
        ]
        for city in CITIES:
            for kw in keywords:
                records.extend(live_scrape(city, kw, pages=3))
        print(f"  [live] Collected {len(records)} records")

    records.extend(simulate_glassdoor(n_per_city=n_per_city))

    df = pd.DataFrame(records)[COLUMNS]
    df = deduplicate(df)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n  [saved] {OUTPUT_PATH}")
    print(f"  Total  : {len(df)} records")
    print(f"\n  City Distribution:")
    print(df["city"].value_counts().to_string())
    print(f"\n  Top 5 Domains:")
    print(df["job_domain"].value_counts().head().to_string())
    return df


if __name__ == "__main__":
    run(use_live=False, n_per_city=300)
