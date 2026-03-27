"""
indeed_scraper.py — Indeed.com Job Data Collector
==================================================
Platform Profile:
  - General job board — widest company mix
  - SMEs + large companies + MNCs
  - All experience levels (fresher to senior)
  - Monthly salary format common
  - High volume of support/operations roles

Live Scraping Method:
  - Selenium WebDriver (headless Chrome)
  - JS-rendered pages handled automatically
  - Pagination via &start=N*10 parameter
  - Polite 3-5s delay between pages

Simulated Data Profile:
  - Widest experience spread (fresher to lead)
  - Most diverse company pool
  - Mix of all IT domains

Output: data/indeed_jobs.csv (~1,199 records)

Run:
    python scrapers/indeed_scraper.py
"""

import os, sys, time, random
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_data import (
    COLUMNS, CITIES, INDEED_COMPANIES, DOMAIN_TECH,
    DOMAIN_TITLES, CITY_DOMAIN_WEIGHTS, build_record,
    deduplicate, random_date, classify_domain,
)

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "indeed_jobs.csv"
)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


# ─────────────────────────────────────────────────────────────
# LIVE SCRAPER — Indeed India (Selenium WebDriver)
# ─────────────────────────────────────────────────────────────
def live_scrape(city: str, keyword: str, pages: int = 6) -> list:
    """
    Scrape Indeed India using Selenium WebDriver.

    URL pattern:
        https://in.indeed.com/jobs?q={keyword}&l={city}&start={n*10}

    Each page has ~10 job cards.
    Selenium handles JavaScript-rendered content.

    Args:
        city    : Target city (e.g. "Surat")
        keyword : Job search keyword (e.g. "Data Analyst")
        pages   : Number of pages to paginate through

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
        print("  [indeed] selenium not installed — using simulator")
        return []

    # ── Headless Chrome setup ─────────────────────────────────
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    jobs   = []

    try:
        for page in range(pages):
            start = page * 10
            url   = (
                f"https://in.indeed.com/jobs"
                f"?q={keyword.replace(' ', '+')}"
                f"&l={city}%2C+Gujarat"
                f"&start={start}"
            )
            print(f"    [indeed-live] Page {page+1}: {url}")
            driver.get(url)

            # Wait for job cards to appear
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "resultContent")
                    )
                )
            except Exception:
                pass

            # Scroll to trigger lazy loading
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)

            # Extract job cards
            for card in driver.find_elements(
                By.CLASS_NAME, "job_seen_beacon"
            ):
                try:
                    title   = card.find_element(By.CLASS_NAME, "jobTitle").text.strip()
                    company = card.find_element(By.CLASS_NAME, "companyName").text.strip()
                    loc     = card.find_element(By.CLASS_NAME, "companyLocation").text.strip()
                    sal_els = card.find_elements(By.CLASS_NAME, "salary-snippet")
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
                            "source_portal"    : "Indeed",
                            "experience_years" : 0.0,
                            "salary_annual_inr": float("nan"),
                        })
                except Exception:
                    continue

            # Polite delay between pages
            time.sleep(random.uniform(3.0, 5.0))

    finally:
        driver.quit()

    print(f"    [indeed-live] Collected {len(jobs)} jobs from {city}")
    return jobs


# ─────────────────────────────────────────────────────────────
# SIMULATOR — Indeed-style realistic data
# ─────────────────────────────────────────────────────────────
def simulate_indeed(n_per_city: int = 325, seed: int = 303) -> list:
    """
    Generate realistic Indeed-style job listings.

    Indeed Profile:
      - Widest range of companies (SMEs + large)
      - Mix of all experience levels
      - Monthly salary format more common
      - High volume of support/operations roles
      - More walk-in and urgent hiring

    Args:
        n_per_city : Records per city (default 325 → 1,300 total)
        seed       : Random seed for reproducibility

    Returns:
        list of job record dicts
    """
    random.seed(seed)
    np.random.seed(seed)

    # Indeed experience distribution — widest spread
    LEVEL_DIST = [
        ("fresher",   0.20),
        ("junior",    0.28),
        ("mid",       0.28),
        ("senior",    0.15),
        ("lead",      0.07),
        ("principal", 0.02),
    ]
    levels_pool   = [l for l, w in LEVEL_DIST
                     for _ in range(int(w * 100))]
    JOB_TYPE_DIST = (
        ["Full-time"]  * 75 +
        ["Contract"]   * 15 +
        ["Internship"] * 7  +
        ["Part-time"]  * 3
    )

    all_records = []

    for city in CITIES:
        companies  = INDEED_COMPANIES[city]
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
                portal    = "Indeed",
                days_back = 75,
                is_intern = (job_type == "Internship"),
            )
            all_records.append(record)

    print(f"  [indeed-sim] Generated {len(all_records)} records")
    return all_records


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def run(use_live: bool = False, n_per_city: int = 325):
    """
    Run Indeed data collection pipeline.

    Args:
        use_live   : If True attempts live scraping first
        n_per_city : Records per city in simulation
    """
    print("=" * 55)
    print("  INDEED SCRAPER")
    print("=" * 55)

    records = []

    # Attempt live scraping if enabled
    if use_live:
        keywords = [
            "IT Jobs", "Software Developer", "Data Analyst",
            "Network Engineer", "Technical Support",
            "Python Developer", "Java Developer",
        ]
        for city in CITIES:
            for kw in keywords:
                records.extend(live_scrape(city, kw, pages=4))
        print(f"  [live] Collected {len(records)} records")

    # Always generate simulated data
    records.extend(simulate_indeed(n_per_city=n_per_city))

    # Build DataFrame, deduplicate, save
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
    run(use_live=False, n_per_city=325)
