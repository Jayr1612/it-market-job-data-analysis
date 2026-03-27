"""
naukri_scraper.py — Naukri.com Data Collector
==============================================
Platform Profile:
  - India's largest job portal
  - Focus: Mid-level to senior IT professionals
  - Salary: Mostly disclosed in LPA
  - Experience: 1-10+ years dominant
  - Companies: Indian IT majors + MNCs

Live Scraping:
  Uses requests + BeautifulSoup
  Handles pagination via ?pageNo=N
  Polite 2-4s delay between requests

Output: data/naukri_jobs.csv (~1,500 records)
"""

import os, sys, time, random, re
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from base_data import (
    COLUMNS, CITIES, NAUKRI_COMPANIES, DOMAIN_TECH,
    DOMAIN_TITLES, CITY_DOMAIN_WEIGHTS, EXPERIENCE_BY_LEVEL,
    build_record, deduplicate, random_date, classify_domain,
)

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "naukri_jobs.csv"
)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ─────────────────────────────────────────────────────────────
# LIVE SCRAPER — Naukri (requests + BeautifulSoup)
# ─────────────────────────────────────────────────────────────
def live_scrape(city: str, keyword: str, pages: int = 8) -> list:
    """
    Scrape Naukri.com for job listings.
    URL pattern: naukri.com/{keyword}-jobs-in-{city}?pageNo={n}
    Each page returns ~20 job cards.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("  requests/bs4 not installed — using simulator")
        return []

    jobs    = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept"         : "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    for page in range(1, pages + 1):
        url = (
            f"https://www.naukri.com/"
            f"{keyword.lower().replace(' ', '-')}-jobs-in-{city.lower()}"
            f"?pageNo={page}"
        )
        print(f"    [naukri-live] Scraping: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"    [naukri-live] HTTP {resp.status_code} — stopping")
                break

            soup  = resp.text
            bs    = BeautifulSoup(soup, "html.parser")

            # Naukri job cards use article.jobTuple or div.srp-jobtuple
            cards = (bs.find_all("article", class_=re.compile(r"jobTuple")) or
                     bs.find_all("div",     class_=re.compile(r"srp-jobtuple")))

            if not cards:
                print(f"    [naukri-live] No cards found on page {page}")
                break

            for card in cards:
                try:
                    title_tag  = card.find("a", class_=re.compile(r"title|jobTitle"))
                    comp_tag   = card.find("a", class_=re.compile(r"subTitle|comp"))
                    exp_tag    = card.find("li", class_=re.compile(r"experience|exp"))
                    sal_tag    = card.find("li", class_=re.compile(r"salary|sal"))
                    loc_tag    = card.find("li", class_=re.compile(r"location|loc"))
                    skill_tags = card.find_all("li", class_=re.compile(r"tag"))

                    title    = title_tag.get_text(strip=True)  if title_tag  else ""
                    company  = comp_tag.get_text(strip=True)   if comp_tag   else ""
                    exp      = exp_tag.get_text(strip=True)    if exp_tag    else ""
                    salary   = sal_tag.get_text(strip=True)    if sal_tag    else "Not Disclosed"
                    location = loc_tag.get_text(strip=True)    if loc_tag    else city
                    skills   = ", ".join(s.get_text(strip=True) for s in skill_tags)

                    if title and company:
                        jobs.append({
                            "job_title"        : title,
                            "company_name"     : company,
                            "location"         : location,
                            "city"             : city,
                            "experience"       : exp,
                            "salary"           : salary,
                            "skills"           : skills,
                            "job_description"  : "",
                            "job_domain"       : classify_domain(title, skills),
                            "job_type"         : "Full-time",
                            "date_posted"      : random_date(30),
                            "source_portal"    : "Naukri",
                            "experience_years" : 0.0,
                            "salary_annual_inr": float("nan"),
                        })
                except Exception:
                    continue

            # Polite delay
            time.sleep(random.uniform(2.5, 4.5))

        except Exception as e:
            print(f"    [naukri-live] Error: {e}")
            break

    return jobs


# ─────────────────────────────────────────────────────────────
# SIMULATOR — Naukri-style data
# Profile: experienced, Indian IT companies, LPA salary
# ─────────────────────────────────────────────────────────────
def simulate_naukri(n_per_city: int = 375, seed: int = 101) -> list:
    """
    Generate realistic Naukri-style job listings.
    Naukri profile:
      - Mostly Full-time roles
      - Mix of freshers + experienced (1-10 yrs)
      - Indian IT companies dominate
      - Salary mostly in LPA format
      - Many tech keywords in listings
    """
    random.seed(seed)
    np.random.seed(seed)

    # Naukri seniority distribution
    LEVEL_DIST = [
        ("fresher",   0.15),
        ("junior",    0.25),
        ("mid",       0.30),
        ("senior",    0.20),
        ("lead",      0.08),
        ("principal", 0.02),
    ]
    levels_pool   = [l for l, w in LEVEL_DIST
                     for _ in range(int(w * 100))]
    JOB_TYPE_DIST = ["Full-time"] * 85 + ["Contract"] * 12 + ["Part-time"] * 3

    all_records = []

    for city in CITIES:
        companies  = NAUKRI_COMPANIES[city]
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
                job_type=job_type, portal="Naukri",
                days_back=60, is_intern=False,
            )
            all_records.append(record)

    print(f"  [naukri-sim] Generated {len(all_records)} records")
    return all_records


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def run(use_live: bool = False, n_per_city: int = 375):
    print("=" * 55)
    print("  NAUKRI SCRAPER")
    print("=" * 55)

    records = []
    if use_live:
        keywords = [
            "Python Developer", "Data Analyst", "Java Developer",
            "DevOps Engineer", "React Developer", "QA Engineer",
        ]
        for city in CITIES:
            for kw in keywords:
                records.extend(live_scrape(city, kw, pages=5))
        print(f"  [live] Collected {len(records)} records")

    # Simulate to supplement / replace
    records.extend(simulate_naukri(n_per_city=n_per_city))

    df = pd.DataFrame(records)[COLUMNS]
    df = deduplicate(df)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n  [saved] {OUTPUT_PATH}")
    print(f"  Total  : {len(df)} records")
    print(f"  Cities : \n{df['city'].value_counts().to_string()}")
    print(f"  Domains (top 5):\n{df['job_domain'].value_counts().head().to_string()}")
    return df


if __name__ == "__main__":
    run(use_live=False, n_per_city=375)
