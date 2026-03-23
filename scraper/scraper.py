"""
scraper.py — IT Job Market Scraper for Gujarat, India
======================================================
Provides:
  1. Live scraper skeletons for Naukri, Indeed, LinkedIn (Selenium/BS4)
  2. Realistic data simulator — generates 3,200+ job records
  3. Data cleaning pipeline
  4. Saves: data/raw_jobs_dataset.csv & data/cleaned_jobs_dataset.csv

Run:
    python scraper/scraper.py
"""

import os, sys, time, random, re, datetime, hashlib
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from utils import (classify_domain, normalize_city, normalize_salary,
                   parse_experience, standardize_skills, deduplicate)

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
RAW_CSV   = os.path.join(DATA_DIR, "raw_jobs_dataset.csv")
CLEAN_CSV = os.path.join(DATA_DIR, "cleaned_jobs_dataset.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION A — LIVE SCRAPER SKELETONS
# Note: LinkedIn/Indeed/Glassdoor block bots. Naukri is most accessible.
# Use simulator (Section B) for reliable data generation.
# ─────────────────────────────────────────────────────────────────────────────

def scrape_naukri(city: str, keyword: str = "IT", pages: int = 5) -> list:
    """Naukri scraper using requests + BeautifulSoup."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("  [naukri] requests/bs4 not installed.")
        return []

    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for page in range(1, pages + 1):
        url = (f"https://www.naukri.com/{keyword.lower().replace(' ','-')}"
               f"-jobs-in-{city.lower()}?pageNo={page}")
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                break
            soup  = BeautifulSoup(resp.text, "html.parser")
            cards = soup.find_all("article", class_=re.compile("jobTuple"))
            for card in cards:
                try:
                    title   = card.find("a",  class_=re.compile("title")).get_text(strip=True)
                    company = card.find("a",  class_=re.compile("subTitle")).get_text(strip=True)
                    exp_tag = card.find("li", class_=re.compile("experience"))
                    sal_tag = card.find("li", class_=re.compile("salary"))
                    loc_tag = card.find("li", class_=re.compile("location"))
                    skills  = " ".join(s.get_text(strip=True) for s in card.find_all("li", class_=re.compile("tag")))
                    jobs.append({"job_title": title, "company_name": company,
                                 "location": loc_tag.get_text(strip=True) if loc_tag else city,
                                 "city": city, "experience": exp_tag.get_text(strip=True) if exp_tag else "",
                                 "salary": sal_tag.get_text(strip=True) if sal_tag else "Not Disclosed",
                                 "skills": skills, "job_description": "", "job_domain": "",
                                 "job_type": "Full-time", "date_posted": str(datetime.date.today()),
                                 "source_portal": "Naukri"})
                except Exception:
                    continue
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"  [naukri] Error: {e}")
            break
    return jobs


def scrape_indeed(city: str, keyword: str = "IT", pages: int = 5) -> list:
    """Indeed scraper using Selenium (handles JS rendering)."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("  [indeed] selenium not installed.")
        return []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    jobs   = []

    try:
        for page in range(0, pages * 10, 10):
            url = f"https://in.indeed.com/jobs?q={keyword.replace(' ','+')}&l={city}&start={page}"
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "jobsearch-ResultsList")))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            for card in driver.find_elements(By.CLASS_NAME, "job_seen_beacon"):
                try:
                    title   = card.find_element(By.CLASS_NAME, "jobTitle").text
                    company = card.find_element(By.CLASS_NAME, "companyName").text
                    loc     = card.find_element(By.CLASS_NAME, "companyLocation").text
                    sal_els = card.find_elements(By.CLASS_NAME, "salary-snippet")
                    jobs.append({"job_title": title, "company_name": company, "location": loc,
                                 "city": city, "experience": "", "salary": sal_els[0].text if sal_els else "Not Disclosed",
                                 "skills": "", "job_description": "", "job_domain": "",
                                 "job_type": "Full-time", "date_posted": str(datetime.date.today()),
                                 "source_portal": "Indeed"})
                except Exception:
                    continue
            time.sleep(random.uniform(3, 6))
    finally:
        driver.quit()
    return jobs


def scrape_linkedin(city: str, keyword: str = "IT", pages: int = 3) -> list:
    """LinkedIn scraper using Selenium."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("  [linkedin] selenium not installed.")
        return []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    jobs   = []

    try:
        for page in range(pages):
            url = (f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
                   f"&location={city}%2C+Gujarat%2C+India&start={page*25}")
            driver.get(url)
            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
            for card in driver.find_elements(By.CLASS_NAME, "base-card"):
                try:
                    title   = card.find_element(By.CLASS_NAME, "base-search-card__title").text
                    company = card.find_element(By.CLASS_NAME, "base-search-card__subtitle").text
                    loc     = card.find_element(By.CLASS_NAME, "job-search-card__location").text
                    jobs.append({"job_title": title, "company_name": company, "location": loc,
                                 "city": city, "experience": "", "salary": "Not Disclosed",
                                 "skills": "", "job_description": "", "job_domain": "",
                                 "job_type": "Full-time", "date_posted": str(datetime.date.today()),
                                 "source_portal": "LinkedIn"})
                except Exception:
                    continue
    finally:
        driver.quit()
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# SECTION B — DATA SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────

CITIES = ["Surat", "Ahmedabad", "Vadodara", "Gandhinagar"]

COMPANIES_BY_CITY = {
    "Surat": ["Tata Consultancy Services","Infosys BPO","Softvan Pvt Ltd","Technosoft Solutions","WebMob Technologies","CMARIX Technolabs","Infowind Technologies","Synarion IT Solutions","Orion InfoSolutions","DigiPrima Technologies","Softobiz Technologies","QSS Technosoft","ValueSoft Technologies","HData Systems","Dev Technosys","Arrant Technologies","IndiaNIC Infotech","Mobisoft Infotech"],
    "Ahmedabad": ["Tata Consultancy Services","Wipro Technologies","HCL Technologies","Infosys Ltd","Cognizant Technology","Zydus Infotech","eSparkBiz Technologies","Bacancy Technology","Mobisoft Infotech","iFour Technolab","Brainium Technologies","WeblineIndia","Sphinx Worldbiz","SoluLab Inc","Elsner Technologies","Capgemini Ahmedabad","Crest Data Systems","L&T Infotech","Deloitte USI","Adani Digital Labs"],
    "Vadodara": ["Wipro Infrastructure Engineering","L&T Technology Services","Tata Technologies","IGATE Corporation","Mastech Digital","Emerson Automation","GE Digital India","Siemens IT","SAP Labs Vadodara","Oracle Vadodara","Syntel Ltd","Larsen & Toubro IT","Hexaware Technologies","KPIT Technologies","Persistent Systems Vadodara"],
    "Gandhinagar": ["GIFT City Fintech Hub","Gujarat State Wide Area Network","National Informatics Centre Gujarat","iCreate Startup Hub","PDPU Innovation Centre","Dhruva Infotech","Gujarat Informatics Ltd","GSWAN Technologies","Torrent Software","Zydus Digital Health","Suzuki Motor Gujarat IT","Gujarat Gas IT Division","ONGC Digital","BPCL IT Division","ISRO IT"],
}

DOMAIN_TECH = {
    "Artificial Intelligence / Machine Learning": [["Python","TensorFlow","PyTorch","scikit-learn","Keras","NLP"],["Python","Machine Learning","Deep Learning","Computer Vision","OpenCV"],["Python","LLM","Hugging Face","Transformers","LangChain","RAG"],["Python","ML Engineer","MLflow","Kubeflow","Feature Store"],["Python","NLP","BERT","GPT","Text Classification","spaCy"]],
    "Data Science": [["Python","R","Statistics","Pandas","NumPy","Matplotlib"],["Python","Data Science","Machine Learning","SQL","Tableau"],["Python","scikit-learn","Statistical Analysis","A/B Testing","Pandas"]],
    "Data Engineering": [["Python","Apache Spark","Kafka","Airflow","AWS","SQL"],["PySpark","Databricks","Snowflake","dbt","BigQuery","Python"],["Python","ETL","Hadoop","Hive","HDFS","Data Pipeline"]],
    "Data Analytics": [["Power BI","SQL","Excel","Python","Data Visualization"],["Tableau","SQL","Python","Google Analytics","Looker"],["Power BI","DAX","SQL Server","Excel","Power Query"]],
    "Web Development": [["React","Node.js","JavaScript","HTML","CSS","MongoDB"],["Angular","TypeScript","Spring Boot","Java","MySQL"],["Vue.js","Laravel","PHP","MySQL","REST API","Docker"],["Next.js","React","Node.js","PostgreSQL","GraphQL","TypeScript"],["Django","Python","PostgreSQL","React","REST API"],["PHP","Laravel","MySQL","JavaScript","jQuery","Bootstrap"]],
    "Mobile App Development": [["Flutter","Dart","Firebase","REST API","Android","iOS"],["React Native","JavaScript","Redux","Firebase","Expo"],["Android","Kotlin","Java","Retrofit","Room","Jetpack"],["iOS","Swift","SwiftUI","Xcode","Core Data"]],
    "DevOps": [["Docker","Kubernetes","Jenkins","AWS","Terraform","Ansible"],["CI/CD","GitHub Actions","Docker","Kubernetes","Prometheus","Grafana"],["GitLab CI","Docker","AWS EKS","Helm","ArgoCD","Terraform"]],
    "Cloud Computing": [["AWS","EC2","S3","Lambda","RDS","CloudFormation"],["Azure","Azure DevOps","ARM Templates","Azure Functions"],["GCP","BigQuery","GKE","Cloud Run","Pub/Sub","Terraform"]],
    "Cybersecurity": [["Network Security","VAPT","Burp Suite","Nmap","Metasploit"],["Ethical Hacking","CEH","OSCP","Kali Linux","Penetration Testing"],["SOC Analyst","SIEM","Splunk","Incident Response","Threat Intelligence"]],
    "Blockchain Development": [["Solidity","Ethereum","Web3.js","Smart Contracts","Hardhat"],["Hyperledger Fabric","Chaincode","Go","Docker","Blockchain"]],
    "Game Development": [["Unity","C#","3D Modeling","Blender","Shader Programming"],["Unreal Engine","C++","Blueprint","Game Design"]],
    "QA / Software Testing": [["Selenium","Python","TestNG","JUnit","Automation Testing"],["Cypress","JavaScript","Postman","API Testing","JIRA"],["Appium","Mobile Testing","Java","TestNG","BDD","Cucumber"],["Manual Testing","JIRA","Test Cases","Bug Reporting","Agile"]],
    "UI / UX Design": [["Figma","Adobe XD","Sketch","Prototyping","Wireframing"],["Figma","User Research","Interaction Design","Usability Testing"],["Adobe Illustrator","Figma","Motion Design","Design Systems"]],
    "Database Administration": [["MySQL","PostgreSQL","Oracle DBA","Performance Tuning","SQL"],["MongoDB","Cassandra","Redis","NoSQL","Database Design"],["SQL Server","SSRS","SSIS","T-SQL","Database Administration"]],
    "Embedded Systems / IoT": [["Embedded C","ARM Cortex","RTOS","Linux","Device Drivers"],["Arduino","Raspberry Pi","IoT","MQTT","Python","C++"],["FPGA","VHDL","Verilog","Xilinx","Embedded Linux"]],
    "Network Engineering": [["Cisco","CCNA","Routing","Switching","OSPF","BGP"],["Network Administration","Firewalls","VPN","LAN","WAN"]],
    "ERP / Enterprise Systems": [["SAP ABAP","SAP FICO","SAP SD","SAP MM","HANA"],["Salesforce","Apex","Lightning","Visualforce","CRM"],["SAP Basis","SAP Hana","SAP BW","SAP S/4HANA","ERP"]],
    "Product Management": [["Product Management","Agile","Scrum","JIRA","Roadmap"],["Product Strategy","Market Research","OKRs","Confluence","Agile"]],
    "Technical Support / IT Operations": [["Technical Support","Windows Server","Active Directory","Help Desk"],["L2 Support","ITIL","ServiceNow","Incident Management","Linux"]],
    "Software Development": [["Java","Spring Boot","Microservices","REST API","MySQL"],["Python","Django","REST API","PostgreSQL","Docker"],["C#",".NET Core","ASP.NET","SQL Server","Angular"],["Go","Microservices","Docker","PostgreSQL","gRPC"]],
}

TITLES_BY_DOMAIN = {
    "Artificial Intelligence / Machine Learning": ["ML Engineer","AI Engineer","Machine Learning Engineer","NLP Engineer","Computer Vision Engineer","Deep Learning Engineer","Generative AI Developer"],
    "Data Science": ["Data Scientist","Senior Data Scientist","Junior Data Scientist","Lead Data Scientist"],
    "Data Engineering": ["Data Engineer","Senior Data Engineer","ETL Developer","Big Data Engineer","Analytics Engineer"],
    "Data Analytics": ["Data Analyst","Business Analyst","BI Developer","Power BI Developer","Tableau Developer"],
    "Web Development": ["Frontend Developer","Backend Developer","Full Stack Developer","React Developer","Angular Developer","Node.js Developer","PHP Developer","Django Developer","Java Full Stack Developer"],
    "Mobile App Development": ["Flutter Developer","Android Developer","iOS Developer","React Native Developer","Mobile App Developer"],
    "DevOps": ["DevOps Engineer","Site Reliability Engineer","CI/CD Engineer","Platform Engineer","Infrastructure Engineer"],
    "Cloud Computing": ["Cloud Engineer","AWS Solutions Architect","Azure Cloud Engineer","GCP Engineer"],
    "Cybersecurity": ["Cybersecurity Analyst","Security Engineer","Penetration Tester","SOC Analyst","Ethical Hacker"],
    "Blockchain Development": ["Blockchain Developer","Smart Contract Developer","Solidity Developer","Web3 Developer"],
    "Game Development": ["Unity Developer","Game Developer","Unreal Engine Developer","Game Programmer"],
    "QA / Software Testing": ["QA Engineer","Automation Test Engineer","SDET","Test Analyst","Performance Test Engineer","QA Lead"],
    "UI / UX Design": ["UI Designer","UX Designer","Product Designer","UI/UX Designer","Interaction Designer"],
    "Database Administration": ["Database Administrator","MySQL DBA","Oracle DBA","SQL Server DBA","NoSQL Engineer"],
    "Embedded Systems / IoT": ["Embedded Software Engineer","Firmware Engineer","IoT Developer","Embedded Linux Engineer"],
    "Network Engineering": ["Network Engineer","Network Administrator","CCNA Engineer","Network Architect"],
    "ERP / Enterprise Systems": ["SAP ABAP Developer","Salesforce Developer","SAP Consultant","Oracle ERP Consultant"],
    "Product Management": ["Product Manager","Technical Product Manager","Product Owner","Scrum Master"],
    "Technical Support / IT Operations": ["IT Support Engineer","Technical Support Analyst","System Administrator","L2 Support Engineer"],
    "Software Development": ["Software Engineer","Senior Software Engineer","Junior Software Developer","Software Developer","Backend Engineer"],
}

EXPERIENCE_LEVELS = ["Fresher / 0-1 years","1-3 years","2-4 years","3-5 years","4-6 years","5-8 years","7-10 years","10+ years"]
JOB_TYPES  = ["Full-time","Full-time","Full-time","Internship","Contract","Part-time"]
PORTALS    = ["Naukri","LinkedIn","Indeed","Glassdoor"]

CITY_DOMAIN_WEIGHTS = {
    "Surat":       {"Web Development":0.18,"Software Development":0.14,"Mobile App Development":0.10,"Data Analytics":0.08,"ERP / Enterprise Systems":0.07,"QA / Software Testing":0.06,"UI / UX Design":0.05,"Technical Support / IT Operations":0.05,"Data Science":0.04,"Artificial Intelligence / Machine Learning":0.04,"Cloud Computing":0.04,"DevOps":0.04,"Database Administration":0.03,"Data Engineering":0.03,"Network Engineering":0.02,"Cybersecurity":0.02,"Embedded Systems / IoT":0.01,"Blockchain Development":0.01,"Product Management":0.01,"Game Development":0.01},
    "Ahmedabad":   {"Web Development":0.13,"Software Development":0.12,"Data Science":0.09,"Data Analytics":0.09,"DevOps":0.08,"Cloud Computing":0.08,"Artificial Intelligence / Machine Learning":0.07,"QA / Software Testing":0.05,"Mobile App Development":0.05,"ERP / Enterprise Systems":0.04,"Cybersecurity":0.04,"Data Engineering":0.04,"UI / UX Design":0.03,"Technical Support / IT Operations":0.03,"Product Management":0.03,"Database Administration":0.02,"Network Engineering":0.01,"Embedded Systems / IoT":0.01,"Blockchain Development":0.01,"Game Development":0.01},
    "Vadodara":    {"Embedded Systems / IoT":0.12,"Software Development":0.11,"ERP / Enterprise Systems":0.10,"Web Development":0.10,"Network Engineering":0.08,"Technical Support / IT Operations":0.07,"Data Analytics":0.06,"QA / Software Testing":0.06,"Database Administration":0.05,"Cloud Computing":0.05,"DevOps":0.04,"Cybersecurity":0.04,"Data Science":0.03,"Mobile App Development":0.03,"Artificial Intelligence / Machine Learning":0.02,"Data Engineering":0.02,"UI / UX Design":0.01,"Product Management":0.01,"Blockchain Development":0.01,"Game Development":0.01},
    "Gandhinagar": {"Cloud Computing":0.12,"Cybersecurity":0.11,"Data Engineering":0.10,"Data Analytics":0.09,"Artificial Intelligence / Machine Learning":0.09,"Software Development":0.08,"DevOps":0.07,"Data Science":0.06,"Network Engineering":0.06,"Technical Support / IT Operations":0.05,"ERP / Enterprise Systems":0.04,"Web Development":0.04,"Database Administration":0.03,"QA / Software Testing":0.02,"Mobile App Development":0.02,"Product Management":0.01,"Embedded Systems / IoT":0.01,"UI / UX Design":0.01,"Blockchain Development":0.01,"Game Development":0.01},
}

SALARY_RANGES = {"Fresher / 0-1 years":(2.5,5.0),"1-3 years":(4.0,8.0),"2-4 years":(6.0,12.0),"3-5 years":(8.0,16.0),"4-6 years":(12.0,22.0),"5-8 years":(16.0,30.0),"7-10 years":(22.0,45.0),"10+ years":(35.0,70.0)}

JOB_DESC_TEMPLATES = [
    "We are looking for a passionate {title} to join our growing team in {city}. You will work with {tech} and collaborate with cross-functional teams to deliver high-quality solutions. Strong problem-solving skills essential.",
    "Exciting opportunity for an experienced {title} at our {city} office. The ideal candidate will have hands-on experience with {tech}, excellent communication skills, and a track record of delivering projects on time.",
    "Join our dynamic IT team as a {title}. Responsibilities include designing, developing, and maintaining solutions using {tech}. Be part of an innovative team solving real-world problems for enterprise clients.",
    "We are hiring a talented {title} for our {city} development centre. You will leverage your expertise in {tech} to build scalable products. B.Tech/MCA preferred. Excellent growth opportunities.",
    "Seeking a motivated {title} to strengthen our {city} team. Experience with {tech} is mandatory. Participate in sprint planning, code reviews, and technical documentation.",
]


def _random_date(days_back=90):
    delta = random.randint(0, days_back)
    return (datetime.date.today() - datetime.timedelta(days=delta)).isoformat()


def _salary_str(exp_level, is_internship):
    if is_internship:
        return f"₹{int(random.uniform(5000,20000)):,}/month"
    lo, hi = SALARY_RANGES.get(exp_level, (5.0, 12.0))
    v1 = round(random.uniform(lo, (lo+hi)/2), 1)
    v2 = round(random.uniform((lo+hi)/2, hi), 1)
    if random.random() < 0.2:
        return "Not Disclosed"
    return f"{v1}-{v2} LPA"


def simulate_jobs(n_per_city=800, seed=42):
    """Generate realistic synthetic IT job listings for Gujarat cities."""
    random.seed(seed)
    np.random.seed(seed)
    all_jobs = []

    for city in CITIES:
        companies = COMPANIES_BY_CITY[city]
        weights   = CITY_DOMAIN_WEIGHTS[city]
        domains   = list(weights.keys())
        dom_probs = [weights[d] for d in domains]

        for _ in range(n_per_city):
            domain  = random.choices(domains, weights=dom_probs)[0]
            title   = random.choice(TITLES_BY_DOMAIN[domain])
            tech    = random.choice(DOMAIN_TECH[domain])
            company = random.choice(companies)
            exp_lvl = random.choice(EXPERIENCE_LEVELS)
            portal  = random.choice(PORTALS)
            jtype   = random.choice(JOB_TYPES)
            if jtype == "Internship":
                exp_lvl = "Fresher / 0-1 years"
            desc = random.choice(JOB_DESC_TEMPLATES).format(title=title, city=city, tech=", ".join(tech[:3]))
            all_jobs.append({
                "job_title": title, "company_name": company,
                "location": f"{city}, Gujarat, India", "city": city,
                "experience": exp_lvl, "salary": _salary_str(exp_lvl, jtype=="Internship"),
                "skills": ", ".join(tech), "job_description": desc,
                "job_domain": domain, "job_type": jtype,
                "date_posted": _random_date(), "source_portal": portal,
            })
    print(f"  [simulator] Generated {len(all_jobs)} records.")
    return all_jobs


# ─────────────────────────────────────────────────────────────────────────────
# SECTION C — CLEANING PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Full data cleaning and enrichment pipeline."""
    print("\n[pipeline] Starting cleaning …")
    print(f"  Input:  {len(df)} records")
    df = deduplicate(df)
    df["city"]             = df["city"].apply(normalize_city)
    df["skills"]           = df["skills"].apply(standardize_skills)
    df["experience_years"] = df["experience"].apply(parse_experience)
    df["salary_annual_inr"]= df["salary"].apply(normalize_salary)
    mask = df["job_domain"].isna() | (df["job_domain"] == "")
    if mask.any():
        df.loc[mask, "job_domain"] = df[mask].apply(
            lambda r: classify_domain(r["job_title"], r["skills"]), axis=1)
    before = len(df)
    df = df.dropna(subset=["job_title","company_name"])
    df = df[df["job_title"].str.strip() != ""]
    print(f"  [drop]   Removed {before-len(df)} invalid records.")
    for col in ["job_title","company_name","location","city","experience","salary","skills","job_type","source_portal"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df = df.reset_index(drop=True)
    print(f"  Output: {len(df)} clean records\n")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# SECTION D — MAIN PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(use_live_scraping=False, n_per_city=800, seed=42):
    """End-to-end pipeline: collect → save raw → clean → save cleaned."""
    print("=" * 60)
    print("  IT Job Market Scraper — Gujarat, India")
    print("=" * 60)

    all_jobs = []
    if use_live_scraping:
        print("\n[scraper] Attempting live scraping …")
        for city in CITIES:
            jobs = scrape_naukri(city, "Python Developer", pages=3)
            all_jobs.extend(jobs)

    print("\n[simulator] Generating synthetic dataset …")
    all_jobs.extend(simulate_jobs(n_per_city=n_per_city, seed=seed))

    # Save raw
    raw_df = pd.DataFrame(all_jobs)
    expected = ["job_title","company_name","location","city","experience","salary","skills","job_description","job_domain","job_type","date_posted","source_portal"]
    for col in expected:
        if col not in raw_df.columns:
            raw_df[col] = ""
    raw_df = raw_df[expected]
    raw_df.to_csv(RAW_CSV, index=False, encoding="utf-8-sig")
    print(f"\n[saved] Raw → {RAW_CSV}  ({len(raw_df)} rows)")

    # Clean & save
    clean_df = clean_dataset(raw_df.copy())
    clean_df.to_csv(CLEAN_CSV, index=False, encoding="utf-8-sig")
    print(f"[saved] Cleaned → {CLEAN_CSV}  ({len(clean_df)} rows)")

    print("\n── City Distribution ─────────────────────────────")
    print(clean_df["city"].value_counts().to_string())
    print("\n── Top 5 Domains ──────────────────────────────────")
    print(clean_df["job_domain"].value_counts().head(5).to_string())
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline(use_live_scraping=False, n_per_city=800, seed=42)
