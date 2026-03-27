# 🔍 IT Job Market Analysis — Gujarat, India

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8+-11557c?style=for-the-badge&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-0.13+-4c8cbf?style=for-the-badge&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Scraping-green?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.18+-43B02A?style=for-the-badge&logo=selenium&logoColor=white)

<br>

> ### ⚠️ EDUCATIONAL PURPOSE DISCLAIMER
> **This project is built strictly for educational and learning purposes.**
> Web scraping skeletons are provided for **learning only**.
> Always respect the Terms of Service of any website before scraping.
> This project is part of a **Data Analytics Internship Portfolio.**

<br>

**A complete end-to-end Python Data Analytics project analyzing the
IT job market across 4 major cities of Gujarat, India.**

[📊 Visualizations](#-sample-visualizations) •
[🏗️ Architecture](#️-project-architecture) •
[📚 Libraries](#-libraries-used) •
[🕷️ Scraping](#️-web-scraping-approach) •
[📈 Analysis](#-exploratory-data-analysis) •
[💡 Insights](#-key-insights)

</div>

---

## 📌 Project Overview

This project demonstrates a **complete data analytics pipeline** from raw data
collection to final insights. It was built as part of a **Data Analytics
Internship** to understand IT hiring trends across Gujarat, India.

### 🎯 What This Project Does

```
Web Scrapping  →  Raw Data Collection  →  Data Storage  →  Data Cleaning  →  Classification  →  EDA  →  Insights
      🕷️                    🗃️               💾               🧹                 🏷️           📊       💡
```

| Step | Task | Output |
|------|------|--------|
| 1 | Web Scraping / Data Simulation | Raw job listings |
| 2 | CSV Storage | Structured datasets |
| 3 | Data Cleaning & Preprocessing | Clean dataset |
| 4 | Domain Classification | 20 IT domains tagged |
| 5 | Exploratory Data Analysis | 13 visualizations |
| 6 | Insights Generation | Market insights report |

---

## ⚠️ Educational Purpose — Important Notice

```
╔══════════════════════════════════════════════════════════════════╗
║                  ⚠️  FOR EDUCATIONAL USE ONLY                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ✅ This project is created for LEARNING and PORTFOLIO purposes  ║
║  ✅ All datasets are SIMULATED (not real scraped data)           ║
║  ✅ Scraper code is for DEMONSTRATION of techniques only         ║
║  ✅ No real user/company data is collected or stored             ║
║  ✅ Built as part of Data Analytics Internship                   ║
║                                                                  ║
║  ❌ Do NOT use scraper code on live websites without permission  ║
║  ❌ Always check robots.txt before scraping any website          ║
║  ❌ Respect Terms of Service of all platforms                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROJECT ARCHITECTURE                         │
│                IT Job Market Analysis — Gujarat                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION LAYER                    │
│                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │  Naukri  │  │ LinkedIn │  │  Indeed  │  │Glassdoor │   │
│   │(BS4+req) │  │(Selenium)│  │(Selenium)│  │(Selenium)│   │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│        │              │              │              │         │
│   ┌────┴──────────────┴──────────────┴──────────┐  │         │
│   │            Internshala Scraper               │  │         │
│   │         (Fresher/Intern focused)             │  │         │
│   └────────────────────┬─────────────────────────┘  │         │
└────────────────────────┼────────────────────────────┘         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                        │
│                                                              │
│   raw_jobs_dataset.csv          (3,200 records)             │
│   cleaned_jobs_dataset.csv      (2,399 records)             │
│   internshala_jobs_dataset.csv  (2,000 records)             │
│   merged_jobs_dataset.csv       (3,968 records) ← FINAL     │
└──────────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  DATA PROCESSING LAYER                       │
│                                                              │
│   utils.py                                                   │
│   ├── classify_domain()    → 20 IT domain classification     │
│   ├── normalize_city()     → City name standardization       │
│   ├── parse_experience()   → String → Numeric conversion     │
│   ├── normalize_salary()   → Salary → Annual INR             │
│   ├── standardize_skills() → Skill name normalization        │
│   └── deduplicate()        → Remove duplicate records        │
└──────────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│               EXPLORATORY DATA ANALYSIS LAYER                │
│                                                              │
│   analysis.ipynb / analysis.py                               │
│   ├── City-wise job distribution                             │
│   ├── Domain-wise hiring trends                              │
│   ├── City × Domain heatmap                                  │
│   ├── Tech stack popularity                                  │
│   ├── Experience level distribution                          │
│   ├── Top hiring companies                                   │
│   ├── Portal-wise job counts                                 │
│   ├── Job type distribution                                  │
│   ├── Salary vs experience                                   │
│   ├── City domain stacked bars                               │
│   ├── Skills per city (4-panel)                              │
│   ├── Jobs posted over time                                  │
│   └── Domain share per city (donuts)                         │
└──────────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    INSIGHTS LAYER                            │
│                                                              │
│   ✅ City specialisations identified                         │
│   ✅ Top skills and domains ranked                           │
│   ✅ Salary bands by experience mapped                       │
│   ✅ Fresher market opportunities found                      │
│   ✅ Portal effectiveness compared                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏙️ Target Cities & Scope

| City | IT Specialisation | Jobs |
|------|-----------------|------|
| **Ahmedabad** | AI/ML, DevOps, Cloud Computing, Data Science | 1,061 |
| **Surat** | Web Development, Mobile Apps, UI/UX Design | 1,037 |
| **Vadodara** | Embedded Systems, ERP, Network Engineering | 921 |
| **Gandhinagar** | Cybersecurity, Cloud, Data Engineering | 949 |

---

## 🌐 Job Portals Covered

| Portal | Scraping Method | Focus Area | Records |
|--------|----------------|------------|---------|
| **Naukri** | requests + BeautifulSoup | Mid & Senior IT roles | 632 |
| **LinkedIn** | Selenium WebDriver | All professional levels | 599 |
| **Indeed** | Selenium WebDriver | General IT jobs | 542 |
| **Glassdoor** | Selenium WebDriver | Company + job listings | 626 |
| **Internshala** | Custom Simulator | Internships & Freshers | 1,569 |

---

## 📁 Project Structure

```
it-market-job-data-analysis/
│
├── 📂 scraper/
│   ├── 🐍 scraper.py                ← Main scraper + data simulator + pipeline
│   ├── 🐍 internshala_scraper.py    ← Internshala scraper + CSV merger
│   └── 🐍 utils.py                  ← All helper functions & domain classifier
│
├── 📂 data/
│   ├── 📊 raw_jobs_dataset.csv           ← Raw data (3,200 records)
│   ├── 📊 cleaned_jobs_dataset.csv       ← Cleaned data (2,399 records)
│   ├── 📊 internshala_jobs_dataset.csv   ← Internshala data (2,000 records)
│   └── 📊 merged_jobs_dataset.csv        ← Final merged data (3,968 records)
│
├── 📂 analysis/
│   └── 📓 analysis.ipynb            ← Complete EDA Jupyter Notebook
│
├── 📂 visualizations/
│   ├── 🖼️ 01_city_job_distribution.png
│   ├── 🖼️ 02_domain_hiring_trends.png
│   ├── 🖼️ 03_city_domain_heatmap.png
│   ├── 🖼️ 04_tech_stack_popularity.png
│   ├── 🖼️ 05_experience_distribution.png
│   ├── 🖼️ 06_top_hiring_companies.png
│   ├── 🖼️ 07_portal_job_counts.png
│   ├── 🖼️ 08_job_type_distribution.png
│   ├── 🖼️ 09_salary_vs_experience.png
│   ├── 🖼️ 10_city_domain_stacked.png
│   ├── 🖼️ 11_skills_per_city.png
│   ├── 🖼️ 12_jobs_over_time.png
│   └── 🖼️ 13_domain_share_per_city.png
│
├── 📄 requirements.txt
├── 📄 .gitignore
└── 📄 README.md
```

---

## 📚 Libraries Used

### 🕷️ Web Scraping Libraries

#### 1. `requests` — HTTP Library
```python
import requests

# Used for sending HTTP requests to job portals
response = requests.get(url, headers=headers, timeout=15)
print(response.status_code)  # 200 = success
html_content = response.text
```
> **Purpose:** Fetches raw HTML content from websites like Naukri.
> Simple and fast for static pages that don't need JavaScript rendering.

---

#### 2. `BeautifulSoup4` — HTML Parser
```python
from bs4 import BeautifulSoup

# Parse HTML and extract job data
soup     = BeautifulSoup(html_content, "html.parser")
job_cards = soup.find_all("article", class_="jobTuple")

for card in job_cards:
    title   = card.find("a", class_="title").get_text(strip=True)
    company = card.find("a", class_="subTitle").get_text(strip=True)
    skills  = card.find("li", class_="tag").get_text(strip=True)
```
> **Purpose:** Parses HTML structure and extracts specific elements
> like job titles, company names, salaries, and skills from Naukri pages.

---

#### 3. `Selenium` — Browser Automation
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup headless Chrome browser
options = Options()
options.add_argument("--headless")          # Run without opening browser
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0...")

driver = webdriver.Chrome(options=options)

# Navigate to LinkedIn jobs
driver.get("https://www.linkedin.com/jobs/search/?keywords=Python&location=Ahmedabad")

# Wait for page to load
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "base-card"))
)

# Scroll to load all listings (infinite scroll)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Extract job cards
cards = driver.find_elements(By.CLASS_NAME, "base-card")
for card in cards:
    title   = card.find_element(By.CLASS_NAME, "base-search-card__title").text
    company = card.find_element(By.CLASS_NAME, "base-search-card__subtitle").text

driver.quit()  # Always close browser after scraping
```
> **Purpose:** Automates a real Chrome browser to handle JavaScript-rendered
> pages on LinkedIn, Indeed, and Glassdoor. Handles infinite scrolling,
> dynamic content loading, and pagination automatically.

---

### 📊 Data Processing Libraries

#### 4. `pandas` — Data Manipulation
```python
import pandas as pd

# Load dataset
df = pd.read_csv('data/merged_jobs_dataset.csv')

# Data cleaning operations used in this project
df = df.drop_duplicates()                           # Remove duplicates
df['city'] = df['city'].str.strip().str.title()     # Normalize city names
df['experience_years'] = df['experience'].str.extract(r'(\d+)').astype(float)
df['salary_annual_inr'] = df['salary'].apply(normalize_salary)

# Analysis operations
city_counts   = df['city'].value_counts()
domain_counts = df['job_domain'].value_counts()
pivot_table   = df.pivot_table(index='job_domain', columns='city',
                                values='job_title', aggfunc='count')
```
> **Purpose:** Core library for all data loading, cleaning, transformation,
> aggregation, and analysis. Used extensively throughout the project for
> every data operation.

---

#### 5. `numpy` — Numerical Computing
```python
import numpy as np

# Used for numerical operations
np.random.seed(42)                    # Reproducible random data
salary_avg = np.mean(salary_array)    # Mean calculation
nan_value  = float("nan")             # NaN for missing salaries
```
> **Purpose:** Supports numerical computations, random number generation
> for data simulation, and handling of missing values (NaN).

---

### 📈 Visualization Libraries

#### 6. `matplotlib` — Core Plotting
```python
import matplotlib.pyplot as plt

# Bar chart example
fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(cities, job_counts, color=['#4E79A7','#F28E2B','#E15759','#76B7B2'])
ax.set_title('IT Jobs by City', fontweight='bold', fontsize=14)
ax.set_xlabel('City')
ax.set_ylabel('Number of Jobs')
plt.tight_layout()
plt.savefig('visualizations/01_city_distribution.png', dpi=130)
plt.show()
```
> **Purpose:** Foundation library for all charts and visualizations.
> Used for bar charts, pie charts, line graphs, histograms, and
> scatter plots throughout the EDA.

---

#### 7. `seaborn` — Statistical Visualization
```python
import seaborn as sns

# Heatmap — City vs Domain
sns.heatmap(pivot_table, annot=True, fmt='d',
            cmap='YlOrRd', linewidths=0.5,
            annot_kws={'size': 9, 'weight': 'bold'})

# Box plot — Salary vs Experience
sns.boxplot(data=df, x='experience', y='salary_lpa',
            palette='Blues')

# Color palettes used
colors = sns.color_palette('Spectral', 20)
colors = sns.color_palette('tab20', 20)
colors = sns.color_palette('coolwarm_r', 30)
```
> **Purpose:** Built on top of matplotlib for more attractive statistical
> charts. Used for heatmaps, box plots, and colour palettes throughout
> the analysis.

---

### 🔧 Supporting Libraries

#### 8. `re` — Regular Expressions
```python
import re

# Extract numbers from experience strings
# "2-4 years" → 2.0
match = re.search(r'(\d+(?:\.\d+)?)', "2-4 years")
years = float(match.group(1))  # → 2.0

# Domain classification keyword matching
pattern = r'\b' + re.escape("machine learning") + r'\b'
if re.search(pattern, "Python Machine Learning Engineer".lower()):
    domain = "Artificial Intelligence / Machine Learning"
```
> **Purpose:** Text pattern matching for parsing experience strings,
> salary values, and keyword-based domain classification.

---

#### 9. `hashlib` — Deduplication
```python
import hashlib

# Create unique fingerprint for each job listing
def generate_job_id(row):
    key = f"{row['job_title']}{row['company_name']}{row['city']}"
    return hashlib.md5(key.lower().encode()).hexdigest()[:12]

# Used to detect and remove duplicate job listings
df['_id'] = df.apply(generate_job_id, axis=1)
df = df.drop_duplicates(subset=['_id'])
```
> **Purpose:** Creates unique fingerprints for each job listing to
> detect and remove duplicates when merging datasets from multiple portals.

---

#### 10. `datetime` — Date Handling
```python
import datetime

# Generate random posting dates for simulation
date = datetime.date.today() - datetime.timedelta(days=30)
date_str = date.isoformat()  # "2026-02-21"

# Convert strings to datetime in analysis
df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
df['week'] = df['date_posted'].dt.to_period('W')
df['month'] = df['date_posted'].dt.to_period('M')
```
> **Purpose:** Handles all date parsing, manipulation, and time-based
> analysis like weekly job posting trends.

---

## 🕷️ Web Scraping Approach

### How Each Portal Was Approached

```
┌─────────────────────────────────────────────────────────┐
│                  SCRAPING STRATEGY                      │
├──────────────┬──────────────────────────────────────────┤
│ Portal       │ Approach                                 │
├──────────────┼──────────────────────────────────────────┤
│ Naukri       │ requests + BeautifulSoup                 │
│              │ → Static HTML parsing                    │
│              │ → Pagination via URL parameters          │
├──────────────┼──────────────────────────────────────────┤
│ LinkedIn     │ Selenium WebDriver                       │
│              │ → Headless Chrome browser                │
│              │ → Infinite scroll handling               │
│              │ → Dynamic content loading                │
├──────────────┼──────────────────────────────────────────┤
│ Indeed       │ Selenium WebDriver                       │
│              │ → JS-rendered pages                      │
│              │ → Pagination via start parameter         │
├──────────────┼──────────────────────────────────────────┤
│ Glassdoor    │ Selenium WebDriver                       │
│              │ → Login-required pages                   │
│              │ → Anti-bot bypass techniques             │
├──────────────┼──────────────────────────────────────────┤
│ Internshala  │ Custom Data Simulator                    │
│              │ → Realistic synthetic data               │
│              │ → Intern/fresher focused                 │
└──────────────┴──────────────────────────────────────────┘
```

### Anti-Bot Handling Techniques (Educational)
```python
# 1. Rotate User-Agent headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

# 2. Add polite delays between requests
import time, random
time.sleep(random.uniform(2, 4))  # 2-4 second delay

# 3. Handle pagination properly
for page in range(1, max_pages + 1):
    url = f"https://naukri.com/jobs?pageNo={page}"

# 4. Graceful error handling
try:
    response = requests.get(url, timeout=15)
    if response.status_code != 200:
        break  # Stop if blocked
except Exception as e:
    print(f"Error: {e}")
    break
```

> ⚠️ **Note:** These techniques are shown for **educational purposes only**.
> Always respect websites' `robots.txt` and Terms of Service.

---

## 🏷️ Domain Classification System

The project automatically classifies every job into one of **20 IT domains**
using keyword matching against job titles and skills:

```python
def classify_domain(job_title, skills):
    """
    Classifies job into IT domain using keyword matching.
    Checks job_title + skills against 20 domain keyword lists.
    Returns first matching domain, defaults to 'Software Development'.
    """
    combined = f"{job_title} {skills}".lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', combined):
                return domain
    return "Software Development"
```

| # | Domain | Example Keywords |
|---|--------|-----------------|
| 1 | AI / Machine Learning | TensorFlow, PyTorch, NLP, LLM, BERT |
| 2 | Data Science | scikit-learn, R, Statistics, Pandas |
| 3 | Data Engineering | Spark, Kafka, Airflow, dbt, Snowflake |
| 4 | Data Analytics | Power BI, Tableau, Looker, DAX |
| 5 | Web Development | React, Angular, Node.js, Django, PHP |
| 6 | Mobile App Dev | Flutter, Kotlin, Swift, React Native |
| 7 | DevOps | Docker, Kubernetes, Terraform, Jenkins |
| 8 | Cloud Computing | AWS, Azure, GCP, Lambda, EC2 |
| 9 | Cybersecurity | VAPT, SIEM, Ethical Hacking, CEH |
| 10 | Blockchain | Solidity, Web3, Ethereum |
| 11 | Game Development | Unity, Unreal Engine, C# Game |
| 12 | QA / Testing | Selenium, Cypress, JMeter |
| 13 | UI / UX Design | Figma, Adobe XD, Prototyping |
| 14 | Database Admin | MySQL DBA, Oracle DBA, PostgreSQL |
| 15 | Embedded / IoT | RTOS, Arduino, FPGA, Embedded C |
| 16 | Network Eng | CCNA, Cisco, BGP, Routing |
| 17 | ERP / Enterprise | SAP, Salesforce, Dynamics 365 |
| 18 | Product Management | Agile, Scrum, JIRA, Roadmap |
| 19 | Technical Support | Helpdesk, ITIL, ServiceNow |
| 20 | Software Dev | Java, Python, C#, Go, Microservices |

---

## 🧹 Data Cleaning Pipeline

```python
def clean_dataset(df):
    """
    Complete data cleaning pipeline:
    """
    # Step 1 — Remove duplicate listings
    df = deduplicate(df)

    # Step 2 — Normalize city names
    # "baroda" → "Vadodara", "ahemdabad" → "Ahmedabad"
    df['city'] = df['city'].apply(normalize_city)

    # Step 3 — Standardize skill names
    # "reactjs" → "React", "nodejs" → "Node.js"
    df['skills'] = df['skills'].apply(standardize_skills)

    # Step 4 — Parse experience to numeric
    # "2-4 years" → 2.0, "Fresher" → 0.0
    df['experience_years'] = df['experience'].apply(parse_experience)

    # Step 5 — Normalize salary to annual INR
    # "6-10 LPA" → 800000.0, "₹15,000/month" → 180000.0
    df['salary_annual_inr'] = df['salary'].apply(normalize_salary)

    # Step 6 — Auto-classify missing domains
    df['job_domain'] = df.apply(
        lambda r: classify_domain(r['job_title'], r['skills'])
        if not r['job_domain'] else r['job_domain'], axis=1
    )

    # Step 7 — Remove invalid records
    df = df.dropna(subset=['job_title', 'company_name'])

    return df.reset_index(drop=True)
```

---

## 📊 Dataset Schema

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `job_title` | str | Flutter Developer | Job listing title |
| `company_name` | str | Infosys Ltd | Hiring company |
| `location` | str | Surat, Gujarat | Full location |
| `city` | str | Surat | Normalised city |
| `experience` | str | 2-4 years | Raw experience |
| `experience_years` | float | 2.0 | Parsed years |
| `salary` | str | 6-10 LPA | Raw salary |
| `salary_annual_inr` | float | 800000.0 | Annual INR |
| `skills` | str | Flutter, Dart, Firebase | Tech stack |
| `job_description` | str | We are looking for… | Full description |
| `job_domain` | str | Mobile App Development | IT domain |
| `job_type` | str | Full-time | Employment type |
| `date_posted` | date | 2026-02-15 | Posting date |
| `source_portal` | str | Naukri | Job portal |

---

## 📊 Dataset Summary

| Dataset | Records | Description |
|---------|---------|-------------|
| `raw_jobs_dataset.csv` | 3,200 | Raw collected data |
| `cleaned_jobs_dataset.csv` | 2,399 | After cleaning & dedup |
| `internshala_jobs_dataset.csv` | 2,000 | Internshala listings |
| `merged_jobs_dataset.csv` | **3,968** | ✅ Final analysis dataset |

---

## 📈 Exploratory Data Analysis

### 13 Visualizations Generated

| # | Chart | Type | Insight |
|---|-------|------|---------|
| 01 | City Job Distribution | Bar + Pie | Which city has most IT jobs |
| 02 | Domain Hiring Trends | Horizontal Bar | Most in-demand IT domains |
| 03 | City × Domain Heatmap | Heatmap | Domain strength per city |
| 04 | Tech Stack Popularity | Bar | Top 30 skills in demand |
| 05 | Experience Distribution | Bar + Histogram | Exp levels required |
| 06 | Top Hiring Companies | Horizontal Bar | Top 20 employers |
| 07 | Portal Job Counts | Bar | Best job portal |
| 08 | Job Type Distribution | Donut | Full-time vs Internship |
| 09 | Salary vs Experience | Box Plot | Salary bands by exp |
| 10 | City Domain Stacked | Stacked Bar | Domain mix per city |
| 11 | Skills per City | 4-panel Bar | City-specific skills |
| 12 | Jobs Over Time | Line + Area | Posting trends |
| 13 | Domain Share per City | 4 Donuts | City specialisations |

---

## 📊 Sample Visualizations

### 1. City-wise Job Distribution
![City Distribution](visualizations/01_city_job_distribution.png)

### 2. IT Domain Hiring Trends
![Domain Trends](visualizations/02_domain_hiring_trends.png)

### 3. City × Domain Heatmap
![Heatmap](visualizations/03_city_domain_heatmap.png)

### 4. Top 30 Tech Skills
![Skills](visualizations/04_tech_stack_popularity.png)

### 5. Salary vs Experience
![Salary](visualizations/09_salary_vs_experience.png)

### 6. Top Hiring Companies
![Companies](visualizations/06_top_hiring_companies.png)

---

## 💡 Key Insights

```
╔═══════════════════════════════════════════════════════════╗
║           KEY FINDINGS — GUJARAT IT JOB MARKET           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  🏆 RANKINGS                                              ║
║     #1 City    → Ahmedabad  (1,061 jobs — 26.7%)         ║
║     #1 Domain  → Web Development  (407 listings)         ║
║     #1 Skill   → Python                                  ║
║     #1 Company → Tata Consultancy Services               ║
║     #1 Portal  → Internshala  (most listings)            ║
║                                                           ║
║  🏙️  CITY SPECIALISATIONS                                 ║
║     Surat       → Web Dev, Mobile Apps, UI/UX            ║
║     Ahmedabad   → AI/ML, DevOps, Cloud, Data Science     ║
║     Vadodara    → Embedded Systems, ERP, Networking      ║
║     Gandhinagar → Cybersecurity, Cloud, Data Eng         ║
║                                                           ║
║  💰 SALARY BANDS (Annual)                                 ║
║     Fresher  (0-1 yr)  → ₹2.5 – 5 LPA                   ║
║     Junior   (1-3 yrs) → ₹4 – 8 LPA                     ║
║     Mid      (3-5 yrs) → ₹8 – 16 LPA                    ║
║     Senior   (5-8 yrs) → ₹16 – 30 LPA                   ║
║     Lead     (7-10 yrs)→ ₹22 – 45 LPA                   ║
║                                                           ║
║  🎓 FRESHER MARKET                                        ║
║     1,256 internships available across Gujarat           ║
║     Best cities  → Ahmedabad & Surat                     ║
║     Best portal  → Internshala                           ║
║     Top domains  → Web Dev, Mobile, Data Analytics       ║
║                                                           ║
║  📈 GROWTH SIGNALS                                        ║
║     AI/ML roles growing fastest in Ahmedabad            ║
║     Cloud roles surging in Gandhinagar (GIFT City)      ║
║     Python + React + SQL = most future-proof stack      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🚀 How to Run This Project

### Option 1 — Google Colab (Recommended)
```python
# Step 1: Upload merged_jobs_dataset.csv to Colab
from google.colab import files
uploaded = files.upload()

# Step 2: Install if needed (most are pre-installed in Colab)
# pip install pandas matplotlib seaborn

# Step 3: Load and analyse
import pandas as pd
df = pd.read_csv('merged_jobs_dataset.csv')
df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
print(f'✅ Loaded {len(df)} records')
df.head()
```

### Option 2 — Local Setup
```bash
# 1. Clone repository
git clone https://github.com/Jayr1612/it-market-job-data-analysis.git
cd it-market-job-data-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate datasets
python scraper/scraper.py
python scraper/internshala_scraper.py

# 4. Open analysis notebook
jupyter notebook analysis/analysis.ipynb
```

---

## 📦 Installation — requirements.txt

```
# Web Scraping
requests==2.31.0
beautifulsoup4==4.12.3
selenium==4.18.1
lxml==5.1.0

# Data Processing
pandas==2.2.1
numpy==1.26.4

# Visualization
matplotlib==3.8.3
seaborn==0.13.2

# Jupyter
jupyter==1.0.0
notebook==7.1.2
ipykernel==6.29.3
```

---

## 🛠️ Complete Tech Stack

| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| Language | Python | 3.10+ | Core language |
| Scraping | requests | 2.31.0 | HTTP requests |
| Scraping | BeautifulSoup4 | 4.12.3 | HTML parsing |
| Scraping | Selenium | 4.18.1 | Browser automation |
| Data | Pandas | 2.2.1 | Data manipulation |
| Data | NumPy | 1.26.4 | Numerical computing |
| Visualization | Matplotlib | 3.8.3 | Core charting |
| Visualization | Seaborn | 0.13.2 | Statistical plots |
| Notebook | Jupyter | 7.1.2 | Interactive analysis |
| Built-in | re | — | Regex / text parsing |
| Built-in | hashlib | — | Deduplication hashing |
| Built-in | datetime | — | Date handling |
| Built-in | os | — | File path management |

---

## 🔮 Future Scope

- [ ] Real-time scraping pipeline with Apache Airflow
- [ ] Interactive Streamlit dashboard
- [ ] NLP-based skill extractor from job descriptions
- [ ] REST API for job market data
- [ ] Power BI / Tableau integration
- [ ] Salary prediction ML model
- [ ] Job demand forecasting model

---

## 👨‍💻 Author

**Jayr — Data Analytics Intern**
- 🐙 GitHub: [@Jayr1612](https://github.com/Jayr1612)

---

## 📝 License & Disclaimer

```
MIT License — Free to use for educational purposes

⚠️  DISCLAIMER:
This project is created SOLELY for educational and portfolio demonstration.
All datasets are synthetically generated and do not represent real job data.
Web scraping code is provided for learning purposes only.
The author does not endorse scraping any website without explicit permission.
Always check and respect the Terms of Service and robots.txt of any website.
```

---

<div align="center">

**⭐ If you found this project helpful, please star the repository!**

*Built with ❤️ for learning Data Analytics — Gujarat, India 🇮🇳*

</div>
