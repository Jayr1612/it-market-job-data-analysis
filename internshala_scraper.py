"""
internshala_scraper.py — Internshala Job Data Collector
========================================================
Platform Profile:
  - India's #1 internship & fresher jobs portal
  - Focus: Internships (55%), Part-time, WFH roles
  - Experience: Mostly 0-1 year (freshers/students)
  - Salary: Stipend-based (₹/month format)
  - Companies: Startups, agencies, SMEs

Live Scraping Method:
  - requests + BeautifulSoup (accessible HTML)
  - Pagination via /page-N in URL
  - Polite 2-3.5s delay between pages
  - URL: internshala.com/internships/{keyword}-internship-in-{city}

Simulated Data Profile:
  - 55% Internships, 20% Full-time, 18% Part-time
  - Fresher/0-1 yr experience dominant
  - Stipend range: ₹4,000 – ₹25,000/month
  - Work From Home options included

Output: data/internshala_jobs.csv (~1,793 records)

Run:
    python scrapers/internshala_scraper.py
"""

import os, sys, time, random
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_data import (
    COLUMNS, CITIES, INTERNSHALA_COMPANIES, DOMAIN_TECH,
    DOMAIN_TITLES, INTERN_TITLES, CITY_DOMAIN_WEIGHTS,
    build_record, deduplicate, random_date, classify_domain,
)

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "internshala_jobs.csv"
)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

WORK_MODES = [
    "Work From Home",
    "Work From Office",
    "Hybrid",
    "Work From Office",
]
DURATIONS  = [
    "1 Month", "2 Months", "3 Months",
    "6 Months", "12 Months",
]


# ─────────────────────────────────────────────────────────────
# LIVE SCRAPER — Internshala (requests + BeautifulSoup)
# ─────────────────────────────────────────────────────────────
def live_scrape(city: str, keyword: str, pages: int = 8) -> list:
    """
    Scrape Internshala using requests + BeautifulSoup.

    Internshala has fairly accessible HTML structure —
    most content is server-rendered without heavy JS.

    URL pattern:
        internshala.com/internships/{keyword}-internship-in-{city}/page-{n}

    Args:
        city    : Target city (e.g. "Surat")
        keyword : Search keyword (e.g. "web development")
        pages   : Number of pages to paginate

    Returns:
        list of job record dicts
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("  [internshala] requests/bs4 not installed — using simulator")
        return []

    jobs    = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    for page in range(1, pages + 1):
        url = (
            f"https://internshala.com/internships/"
            f"{keyword.lower().replace(' ', '-')}-internship-in-"
            f"{city.lower()}/page-{page}"
        )
        print(f"    [internshala-live] Page {page}: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"    [internshala-live] HTTP {resp.status_code} — stopping")
                break

            bs    = BeautifulSoup(resp.text, "html.parser")
            cards = bs.find_all(
                "div",
                class_=lambda c: c and "individual_internship" in c
            )

            if not cards:
                print(f"    [internshala-live] No cards on page {page}")
                break

            for card in cards:
                try:
                    title_tag   = card.find("h3", class_="profile")
                    company_tag = card.find("h4", class_="company_name")
                    stipend_tag = card.find("span", class_=lambda c: c and "stipend" in c)
                    dur_tag     = card.find("div", class_=lambda c: c and "duration" in c)
                    skill_tags  = card.find_all("span", class_="round_tabs")

                    title    = title_tag.get_text(strip=True)   if title_tag   else ""
                    company  = company_tag.get_text(strip=True) if company_tag else ""
                    stipend  = stipend_tag.get_text(strip=True) if stipend_tag else "Not Disclosed"
                    duration = dur_tag.get_text(strip=True)     if dur_tag     else "3 Months"
                    skills   = ", ".join(s.get_text(strip=True) for s in skill_tags)

                    if title and company:
                        jobs.append({
                            "job_title"        : title + " Intern",
                            "company_name"     : company,
                            "location"         : f"{city}, Gujarat, India",
                            "city"             : city,
                            "experience"       : "Fresher / 0-1 years",
                            "salary"           : stipend,
                            "skills"           : skills,
                            "job_description"  : (
                                f"Internship at {company} in {city}. "
                                f"Duration: {duration}."
                            ),
                            "job_domain"       : classify_domain(title, skills),
                            "job_type"         : "Internship",
                            "date_posted"      : random_date(30),
                            "source_portal"    : "Internshala",
                            "experience_years" : 0.0,
                            "salary_annual_inr": float("nan"),
                        })
                except Exception:
                    continue

            # Polite delay
            time.sleep(random.uniform(2.0, 3.5))

        except Exception as e:
            print(f"    [internshala-live] Error: {e}")
            break

    print(f"    [internshala-live] Collected {len(jobs)} from {city}")
    return jobs


# ─────────────────────────────────────────────────────────────
# SIMULATOR — Internshala-style realistic data
# ─────────────────────────────────────────────────────────────
def simulate_internshala(n_per_city: int = 500, seed: int = 505) -> list:
    """
    Generate realistic Internshala-style job listings.

    Internshala Profile:
      - 55% Internships, 20% Full-time, 18% Part-time, 7% Contract
      - Mostly fresher/0-1 yr experience
      - Stipend-based salary (₹/month)
      - Startup companies dominate
      - WFH/Hybrid options common
      - Student-friendly beginner tech stacks

    Args:
        n_per_city : Records per city (default 500 → 2,000 total)
        seed       : Random seed

    Returns:
        list of job record dicts
    """
    random.seed(seed)
    np.random.seed(seed)

    JOB_TYPE_DIST   = (
        ["Internship"] * 55 +
        ["Full-time"]  * 20 +
        ["Part-time"]  * 18 +
        ["Contract"]   * 7
    )
    # Internshala = mostly freshers
    LEVEL_DIST_FULL = ["fresher"] * 80 + ["junior"] * 20

    all_records = []

    for city in CITIES:
        companies  = INTERNSHALA_COMPANIES[city]
        weights    = CITY_DOMAIN_WEIGHTS[city]
        domains    = list(weights.keys())
        dom_probs  = [weights[d] for d in domains]

        for _ in range(n_per_city):
            domain   = random.choices(domains, weights=dom_probs)[0]
            job_type = random.choice(JOB_TYPE_DIST)
            is_intern = job_type == "Internship"

            # Intern-specific titles for internship roles
            if is_intern:
                title_pool = INTERN_TITLES.get(
                    domain,
                    INTERN_TITLES.get("Software Development", ["Intern"])
                )
                title = random.choice(title_pool)
                level = "fresher"
            else:
                title = random.choice(DOMAIN_TITLES[domain])
                level = random.choice(LEVEL_DIST_FULL)

            tech     = random.choice(DOMAIN_TECH[domain])
            company  = random.choice(companies)
            mode     = random.choice(WORK_MODES)
            duration = random.choice(DURATIONS)

            record   = build_record(
                job_title = title,
                company   = company,
                city      = city,
                domain    = domain,
                tech      = tech,
                level     = level,
                job_type  = job_type,
                portal    = "Internshala",
                days_back = 45,
                is_intern = is_intern,
                duration  = duration,
            )
            # Add work mode to location string
            record["location"] = f"{city}, Gujarat ({mode})"
            all_records.append(record)

    print(f"  [internshala-sim] Generated {len(all_records)} records")
    return all_records


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def run(use_live: bool = False, n_per_city: int = 500):
    """
    Run Internshala data collection pipeline.

    Args:
        use_live   : If True attempts live scraping first
        n_per_city : Records per city in simulation
    """
    print("=" * 55)
    print("  INTERNSHALA SCRAPER")
    print("=" * 55)

    records = []

    if use_live:
        keywords = [
            "web development", "data science", "python",
            "flutter", "machine learning", "data analytics",
            "android development", "ui ux design",
            "java", "react", "sql", "digital marketing",
        ]
        for city in CITIES:
            for kw in keywords:
                records.extend(live_scrape(city, kw, pages=5))
        print(f"  [live] Collected {len(records)} records")

    records.extend(simulate_internshala(n_per_city=n_per_city))

    df = pd.DataFrame(records)[COLUMNS]
    df = deduplicate(df)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n  [saved] {OUTPUT_PATH}")
    print(f"  Total  : {len(df)} records")
    print(f"\n  City Distribution:")
    print(df["city"].value_counts().to_string())
    print(f"\n  Job Types:")
    print(df["job_type"].value_counts().to_string())
    print(f"\n  Top 5 Domains:")
    print(df["job_domain"].value_counts().head().to_string())
    return df


if __name__ == "__main__":
    run(use_live=False, n_per_city=500)
