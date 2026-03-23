"""
internshala_scraper.py — Internshala Data Generator & CSV Merger
=================================================================
Generates realistic Internshala-style dataset focused on:
  - Internships (stipend-based)
  - Fresher jobs (0-1 year experience)
  - Part-time & Work-from-home roles

Then merges with cleaned_jobs_dataset.csv to create
merged_jobs_dataset.csv (3,968 total records)

Run:
    python scraper/internshala_scraper.py
"""

import os, sys, random, datetime
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from utils import classify_domain, normalize_city, parse_experience, normalize_salary, standardize_skills

BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR        = os.path.join(BASE_DIR, "data")
EXISTING_CSV    = os.path.join(DATA_DIR, "cleaned_jobs_dataset.csv")
INTERNSHALA_CSV = os.path.join(DATA_DIR, "internshala_jobs_dataset.csv")
MERGED_CSV      = os.path.join(DATA_DIR, "merged_jobs_dataset.csv")
os.makedirs(DATA_DIR, exist_ok=True)

CITIES = ["Surat", "Ahmedabad", "Vadodara", "Gandhinagar"]

COMPANIES_BY_CITY = {
    "Surat":       ["DigiGrowth Solutions","CodeCraft Studio","PixelMind Technologies","StartupNest Surat","WebCraft Agency","AppBrew Technologies","DataHive Solutions","TechSprint Labs","InnovateX Surat","Clickable Technologies","SkyNet Solutions","ByteForge Studio","Nexus IT Hub","SmartDev Solutions","ClearCode Technologies","Growthify Digital","ZeroToOne Labs","MindBridge IT"],
    "Ahmedabad":   ["Ahmedabad Startup Hub","TechVenture Gujarat","InnovateTech AMC","DigitalEdge Solutions","CloudNine Technologies","DataFirst Analytics","AI Garage Ahmedabad","Launchpad Technologies","GrowStack IT","ScaleUp Solutions","BrainBox Labs","Technovia Consulting","Agilify Solutions","DevMasters India","PivotTech Gujarat","QuantumLeap IT","FutureBuild Technologies","NexaCode Labs"],
    "Vadodara":    ["Baroda Tech Park","Vadodara IT Solutions","TechBridge Baroda","EmbedSoft Solutions","IndusTech Vadodara","SystemWise IT","ConnectIT Baroda","NetCraft Solutions","CoreLogic Technologies","SmartSys Vadodara","TechOps India","InfraCode Labs"],
    "Gandhinagar": ["GIFT City Startup","iCreate Intern Hub","GovTech Gujarat","CyberShield Gandhinagar","DataGov Solutions","CloudGov IT","SecureNet Gandhinagar","Analytics India GN","PolicyTech Solutions","SmartCity IT Hub","NIC Gujarat Interns","eGov Technologies"],
}

TITLES_BY_DOMAIN = {
    "Web Development":           ["Web Development Intern","Frontend Development Intern","Full Stack Development Intern","React Developer Intern","WordPress Developer Intern","Junior Web Developer","HTML/CSS Developer Intern"],
    "Mobile App Development":    ["Android Development Intern","Flutter Development Intern","iOS Development Intern","React Native Intern","Mobile App Development Intern"],
    "Data Science":              ["Data Science Intern","Machine Learning Intern","AI/ML Intern","Data Science Trainee","Junior Data Scientist"],
    "Data Analytics":            ["Data Analytics Intern","Business Analytics Intern","Power BI Intern","Excel & Data Analyst Intern","Junior Data Analyst"],
    "Data Engineering":          ["Data Engineering Intern","ETL Developer Intern","SQL Developer Intern","Database Intern"],
    "Artificial Intelligence / Machine Learning": ["AI Research Intern","Machine Learning Intern","NLP Intern","Computer Vision Intern","Deep Learning Intern"],
    "DevOps":                    ["DevOps Intern","Cloud & DevOps Trainee","Linux Admin Intern","CI/CD Intern"],
    "Cloud Computing":           ["Cloud Computing Intern","AWS Cloud Intern","Azure Intern","Cloud Support Intern"],
    "Cybersecurity":             ["Cybersecurity Intern","Ethical Hacking Intern","Network Security Intern","Security Analyst Intern"],
    "QA / Software Testing":     ["Software Testing Intern","QA Intern","Manual Testing Intern","Automation Testing Intern","Test Engineer Trainee"],
    "UI / UX Design":            ["UI/UX Design Intern","Graphic & UI Design Intern","Product Design Intern","Figma Design Intern"],
    "Software Development":      ["Software Development Intern","Java Developer Intern","Python Developer Intern","C++ Developer Intern","Junior Software Engineer","Backend Development Intern"],
    "Technical Support / IT Operations": ["IT Support Intern","Technical Support Trainee","Helpdesk Intern","System Admin Intern"],
    "Product Management":        ["Product Management Intern","Business Analyst Intern","Product Design Intern"],
    "Blockchain Development":    ["Blockchain Development Intern","Web3 Intern","Smart Contract Intern"],
    "Game Development":          ["Game Development Intern","Unity Developer Intern","Game Design Intern"],
    "Embedded Systems / IoT":    ["Embedded Systems Intern","IoT Development Intern","Hardware & Software Intern"],
    "Network Engineering":       ["Network Engineering Intern","CCNA Trainee","Network Support Intern"],
    "ERP / Enterprise Systems":  ["SAP Intern","ERP Support Intern","Salesforce Intern","Oracle ERP Trainee"],
    "Database Administration":   ["Database Intern","SQL Developer Intern","MySQL Admin Intern"],
}

TECH_BY_DOMAIN = {
    "Web Development":           [["HTML","CSS","JavaScript","Bootstrap"],["React","HTML","CSS","JavaScript","Git"],["PHP","MySQL","HTML","CSS","JavaScript"],["Django","Python","HTML","CSS","SQLite"]],
    "Mobile App Development":    [["Flutter","Dart","Firebase"],["Android","Java","XML","Firebase"],["React Native","JavaScript","Expo"]],
    "Data Science":              [["Python","Pandas","NumPy","Matplotlib"],["Python","scikit-learn","Jupyter Notebook"],["Python","TensorFlow","Keras","Pandas"]],
    "Data Analytics":            [["Excel","Power BI","SQL"],["Tableau","SQL","Excel","Google Sheets"],["Python","Pandas","Matplotlib","SQL"]],
    "Data Engineering":          [["SQL","Python","MySQL","ETL Basics"],["Python","Pandas","PostgreSQL"]],
    "Artificial Intelligence / Machine Learning": [["Python","Machine Learning","scikit-learn","Pandas"],["Python","TensorFlow","Keras","NumPy"],["Python","NLP","NLTK","spaCy"]],
    "DevOps":                    [["Linux","Bash","Git","Docker Basics"],["Docker","Jenkins","Git","Linux"]],
    "Cloud Computing":           [["AWS Basics","S3","EC2","IAM"],["Azure Fundamentals","Cloud Concepts"]],
    "Cybersecurity":             [["Network Security","Kali Linux","Nmap"],["Ethical Hacking","Wireshark","Linux"]],
    "QA / Software Testing":     [["Manual Testing","JIRA","Test Cases"],["Selenium","Java","TestNG","JUnit"],["Postman","API Testing","SQL"]],
    "UI / UX Design":            [["Figma","Adobe XD","Canva"],["Figma","Prototyping","Wireframing"]],
    "Software Development":      [["Java","OOP","Data Structures","MySQL"],["Python","Flask","SQLite","REST API"],["C++","DSA","OOP","Linux"]],
    "Technical Support / IT Operations": [["Windows","Networking Basics","Hardware"],["Linux","Troubleshooting","MS Office"]],
    "Product Management":        [["Product Thinking","JIRA","Agile Basics"],["Market Research","Excel","Presentation"]],
    "Blockchain Development":    [["Solidity Basics","Ethereum","Web3.js"],["Blockchain Fundamentals","Python","Cryptography"]],
    "Game Development":          [["Unity","C# Basics","2D Game Design"],["Python","Pygame","Game Logic"]],
    "Embedded Systems / IoT":    [["Arduino","C","Electronics Basics"],["Raspberry Pi","Python","IoT Sensors"]],
    "Network Engineering":       [["CCNA Basics","Cisco Packet Tracer","TCP/IP"],["Networking Fundamentals","Wireshark","Linux"]],
    "ERP / Enterprise Systems":  [["SAP Basics","ERP Concepts","Excel"],["Salesforce Basics","CRM Concepts"]],
    "Database Administration":   [["MySQL","SQL","Database Design"],["PostgreSQL","SQL","Python"],["MongoDB","NoSQL Basics","JavaScript"]],
}

CITY_DOMAIN_WEIGHTS = {
    "Surat":       {"Web Development":0.20,"Software Development":0.12,"Mobile App Development":0.10,"UI / UX Design":0.08,"Data Analytics":0.07,"QA / Software Testing":0.07,"Data Science":0.05,"Artificial Intelligence / Machine Learning":0.05,"Technical Support / IT Operations":0.05,"Cloud Computing":0.04,"DevOps":0.04,"Cybersecurity":0.03,"Blockchain Development":0.02,"Game Development":0.02,"Embedded Systems / IoT":0.01,"Network Engineering":0.01,"ERP / Enterprise Systems":0.01,"Product Management":0.01,"Data Engineering":0.01,"Database Administration":0.01},
    "Ahmedabad":   {"Artificial Intelligence / Machine Learning":0.12,"Data Science":0.10,"Web Development":0.10,"Software Development":0.10,"Data Analytics":0.08,"DevOps":0.07,"Cloud Computing":0.07,"Mobile App Development":0.06,"QA / Software Testing":0.05,"UI / UX Design":0.05,"Cybersecurity":0.04,"Product Management":0.04,"Blockchain Development":0.03,"Data Engineering":0.03,"Technical Support / IT Operations":0.02,"Game Development":0.01,"Network Engineering":0.01,"Embedded Systems / IoT":0.01,"ERP / Enterprise Systems":0.01,"Database Administration":0.01},
    "Vadodara":    {"Embedded Systems / IoT":0.14,"Software Development":0.12,"Web Development":0.10,"Network Engineering":0.08,"ERP / Enterprise Systems":0.08,"QA / Software Testing":0.07,"Technical Support / IT Operations":0.07,"Data Analytics":0.06,"Database Administration":0.05,"Cloud Computing":0.04,"DevOps":0.04,"Cybersecurity":0.04,"Data Science":0.04,"Mobile App Development":0.03,"UI / UX Design":0.02,"Artificial Intelligence / Machine Learning":0.01,"Blockchain Development":0.01,"Game Development":0.01,"Product Management":0.01,"Data Engineering":0.01},
    "Gandhinagar": {"Cloud Computing":0.12,"Cybersecurity":0.12,"Data Engineering":0.10,"Data Analytics":0.09,"Artificial Intelligence / Machine Learning":0.09,"Software Development":0.08,"DevOps":0.07,"Network Engineering":0.07,"Technical Support / IT Operations":0.05,"Data Science":0.05,"ERP / Enterprise Systems":0.04,"Web Development":0.04,"Database Administration":0.03,"QA / Software Testing":0.02,"Mobile App Development":0.01,"UI / UX Design":0.01,"Product Management":0.01,"Embedded Systems / IoT":0.01,"Blockchain Development":0.01,"Game Development":0.01},
}

STIPEND_RANGES = {"Internship":(3000,20000),"Part-time":(5000,25000),"Full-time":(15000,50000)}
WORK_MODES     = ["Work From Home","Work From Office","Hybrid","Work From Office"]
DURATIONS      = ["1 Month","2 Months","3 Months","6 Months","12 Months"]
JOB_TYPES      = ["Internship","Full-time","Part-time","Contract"]
JOB_WEIGHTS    = [0.55, 0.25, 0.15, 0.05]

DESC_TEMPLATES = [
    "We are looking for a passionate {title} in {city}. Great opportunity for students to gain hands-on experience with {tech}. Certificate provided.",
    "Exciting {duration} internship at our {city} office! Learn {tech} on real projects. PPO for outstanding performers.",
    "Join our startup as {title} and learn {tech} from industry experts in {city}. Friendly culture, mentorship, hands-on experience.",
    "Apply for {title} at our {city} company! Work on projects using {tech}. Duration: {duration}. Stipend provided.",
]


def _random_date(days_back=60):
    return (datetime.date.today() - datetime.timedelta(days=random.randint(0, days_back))).isoformat()


def _stipend_str(job_type):
    lo, hi = STIPEND_RANGES.get(job_type, (5000, 15000))
    amt    = round(random.randint(lo, hi) / 500) * 500
    if random.random() < 0.1:
        return "Unpaid / Certificate Only"
    return f"₹{amt:,}/month (Stipend)" if job_type == "Internship" else f"₹{amt:,}/month"


def simulate_internshala(n_per_city=500, seed=99):
    """Generate realistic Internshala-style job listings."""
    random.seed(seed)
    np.random.seed(seed)
    all_jobs = []

    for city in CITIES:
        companies = COMPANIES_BY_CITY[city]
        weights   = CITY_DOMAIN_WEIGHTS[city]
        domains   = list(weights.keys())
        dom_probs = [weights[d] for d in domains]

        for _ in range(n_per_city):
            domain   = random.choices(domains, weights=dom_probs)[0]
            title    = random.choice(TITLES_BY_DOMAIN.get(domain, TITLES_BY_DOMAIN["Software Development"]))
            tech     = random.choice(TECH_BY_DOMAIN.get(domain, TECH_BY_DOMAIN["Software Development"]))
            company  = random.choice(companies)
            job_type = random.choices(JOB_TYPES, weights=JOB_WEIGHTS)[0]
            duration = random.choice(DURATIONS)
            mode     = random.choice(WORK_MODES)
            stipend  = _stipend_str(job_type)
            exp      = "Fresher / 0-1 years"
            exp_yrs  = 0.0
            if job_type == "Full-time":
                exp     = random.choice(["Fresher / 0-1 years","1-3 years"])
                exp_yrs = 0.0 if "Fresher" in exp else 1.0
            desc = random.choice(DESC_TEMPLATES).format(title=title, city=city, tech=", ".join(tech[:3]), duration=duration)
            all_jobs.append({
                "job_title": title, "company_name": company,
                "location": f"{city}, Gujarat, India ({mode})", "city": city,
                "experience": exp, "salary": stipend,
                "skills": ", ".join(tech), "job_description": desc,
                "job_domain": domain, "job_type": job_type,
                "date_posted": _random_date(), "source_portal": "Internshala",
                "experience_years": exp_yrs, "salary_annual_inr": float("nan"),
            })

    print(f"  [internshala] Generated {len(all_jobs)} records.")
    return all_jobs


def merge_datasets(existing_csv, new_df):
    """Merge existing cleaned CSV with new Internshala DataFrame."""
    print("\n[merge] Loading existing dataset …")
    existing = pd.read_csv(existing_csv)
    print(f"  Existing : {len(existing)}")
    print(f"  New      : {len(new_df)}")

    for col in existing.columns:
        if col not in new_df.columns:
            new_df[col] = ""
    new_df  = new_df[existing.columns]
    merged  = pd.concat([existing, new_df], ignore_index=True)
    merged["_dup_key"] = (merged["job_title"].str.lower().str.strip() + "|" +
                          merged["company_name"].str.lower().str.strip() + "|" +
                          merged["city"].str.lower().str.strip())
    before  = len(merged)
    merged  = merged.drop_duplicates(subset=["_dup_key"]).drop(columns=["_dup_key"])
    print(f"  Merged   : {len(merged)} (removed {before-len(merged)} duplicates)")
    return merged.reset_index(drop=True)


def run():
    print("=" * 60)
    print("  Internshala Generator & CSV Merger")
    print("=" * 60)

    print("\n[Step 1] Generating Internshala dataset …")
    jobs    = simulate_internshala(n_per_city=500, seed=99)
    intr_df = pd.DataFrame(jobs)
    intr_df.to_csv(INTERNSHALA_CSV, index=False, encoding="utf-8-sig")
    print(f"[saved] Internshala CSV → {INTERNSHALA_CSV}")

    print("\n[Step 2] Merging with existing cleaned dataset …")
    merged_df = merge_datasets(EXISTING_CSV, intr_df.copy())
    merged_df.to_csv(MERGED_CSV, index=False, encoding="utf-8-sig")
    print(f"[saved] Merged CSV → {MERGED_CSV}")

    print("\n" + "=" * 60)
    print(f"  Total Records  : {len(merged_df)}")
    print("\n── City Distribution ─────────────────────────────")
    print(merged_df["city"].value_counts().to_string())
    print("\n── Portal Sources ────────────────────────────────")
    print(merged_df["source_portal"].value_counts().to_string())
    print("\n── Job Types ─────────────────────────────────────")
    print(merged_df["job_type"].value_counts().to_string())
    print("=" * 60)
    print("\n✅ Done! Upload merged_jobs_dataset.csv to Colab.")


if __name__ == "__main__":
    run()
