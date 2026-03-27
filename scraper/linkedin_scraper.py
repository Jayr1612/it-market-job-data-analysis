"""
linkedin_scraper.py — LinkedIn Job Data Collector
==================================================
Platform Profile:
  - Professional networking + jobs
  - Focus: Senior roles, MNCs, product companies
  - Salary: Often not disclosed or in USD/LPA
  - Experience: 2-15+ years
  - Companies: MNCs, funded startups, tech giants

Live Scraping:
  Uses Selenium WebDriver (headless Chrome)
  Handles infinite scroll & dynamic content
  Pagination via &start=N parameter

Output: data/linkedin_jobs.csv (~1,200 records)
"""

import os, sys, time, random
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from base_data import (
    COLUMNS, CITIES, LINKEDIN_COMPANIES, DOMAIN_TECH,
    DOMAIN_TITLES, CITY_DOMAIN_WEIGHTS, build_record,
    deduplicate, random_date, classify_domain,
)

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "linkedin_jobs.csv"
)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ─────────────────────────────────────────────────────────────
# LIVE SCRAPER — LinkedIn (Selenium)
# ─────────────────────────────────────────────────────────────
def live_scrape(city: str, keyword: str, pages: int = 5) -> list:
    """
    Scrape LinkedIn jobs using Selenium WebDriver.
    Handles JS-rendered content and infinite scroll.
    URL: linkedin.com/jobs/search/?keywords=X&location=Y&start=N
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("  selenium not installed — using simulator")
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
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    jobs   = []

    try:
        for page in range(pages):
            start = page * 25
            url   = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={keyword.replace(' ', '%20')}"
                f"&location={city}%2C%20Gujarat%2C%20India"
                f"&start={start}"
            )
            print(f"    [linkedin-live] Page {page+1}: {url}")
            driver.get(url)

            # Wait for job cards
            try:
                WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "jobs-search__results-list")
                    )
                )
            except Exception:
                pass

            # Scroll to load all cards
            for _ in range(5):
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(1.5)

            cards = driver.find_elements(By.CLASS_NAME, "base-card")
            for card in cards:
                try:
                    title   = card.find_element(By.CLASS_NAME, "base-search-card__title").text.strip()
                    company = card.find_element(By.CLASS_NAME, "base-search-card__subtitle").text.strip()
                    loc     = card.find_element(By.CLASS_NAME, "job-search-card__location").text.strip()

                    # Try get listed time
                    try:
                        listed = card.find_element(By.CLASS_NAME, "job-search-card__listdate").text.strip()
                    except Exception:
                        listed = ""

                    if title and company:
                        jobs.append({
                            "job_title"        : title,
                            "company_name"     : company,
                            "location"         : loc,
                            "city"             : city,
                            "experience"       : "",
                            "salary"           : "Not Disclosed",
                            "skills"           : "",
                            "job_description"  : "",
                            "job_domain"       : classify_domain(title, ""),
                            "job_type"         : "Full-time",
                            "date_posted"      : random_date(30),
                            "source_portal"    : "LinkedIn",
                            "experience_years" : 0.0,
                            "salary_annual_inr": float("nan"),
                        })
                except Exception:
                    continue

            time.sleep(random.uniform(3.0, 5.0))

    finally:
        driver.quit()

    return jobs


# ─────────────────────────────────────────────────────────────
# SIMULATOR — LinkedIn-style data
# Profile: MNCs, senior roles, higher salaries, less salary disclosure
# ─────────────────────────────────────────────────────────────
def simulate_linkedin(n_per_city: int = 300, seed: int = 202) -> list:
    """
    Generate LinkedIn-style job listings.
    LinkedIn profile:
      - Higher seniority than Naukri
      - MNCs and funded startups dominate
      - More Not Disclosed salaries (40%)
      - More Contract and remote roles
      - Strong in AI/ML, Cloud, DevOps
    """
    random.seed(seed)
    np.random.seed(seed)

    # LinkedIn skews senior
    LEVEL_DIST = [
        ("fresher",   0.05),
        ("junior",    0.15),
        ("mid",       0.30),
        ("senior",    0.30),
        ("lead",      0.15),
        ("principal", 0.05),
    ]
    levels_pool   = [l for l, w in LEVEL_DIST
                     for _ in range(int(w * 100))]
    JOB_TYPE_DIST = (["Full-time"] * 70 + ["Contract"] * 20 +
                     ["Part-time"] * 5 + ["Internship"] * 5)

    all_records = []

    for city in CITIES:
        companies  = LINKEDIN_COMPANIES[city]
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
                job_title=title, company=company, city=city,
                domain=domain, tech=tech, level=level,
                job_type=job_type, portal="LinkedIn",
                days_back=45, is_intern=(job_type == "Internship"),
            )
            all_records.append(record)

    print(f"  [linkedin-sim] Generated {len(all_records)} records")
    return all_records


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def run(use_live: bool = False, n_per_city: int = 300):
    print("=" * 55)
    print("  LINKEDIN SCRAPER")
    print("=" * 55)

    records = []
    if use_live:
        keywords = [
            "Software Engineer", "Data Scientist", "Cloud Architect",
            "DevOps Engineer", "Product Manager", "ML Engineer",
        ]
        for city in CITIES:
            for kw in keywords:
                records.extend(live_scrape(city, kw, pages=4))
        print(f"  [live] Collected {len(records)} records")

    records.extend(simulate_linkedin(n_per_city=n_per_city))

    df = pd.DataFrame(records)[COLUMNS]
    df = deduplicate(df)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n  [saved] {OUTPUT_PATH}")
    print(f"  Total  : {len(df)} records")
    print(f"  Cities : \n{df['city'].value_counts().to_string()}")
    print(f"  Domains (top 5):\n{df['job_domain'].value_counts().head().to_string()}")
    return df


if __name__ == "__main__":
    run(use_live=False, n_per_city=300)
