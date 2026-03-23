"""
utils.py — Helper Functions for IT Job Market Scraper
======================================================
Contains:
  - Domain classification (keyword-based, 20 IT domains)
  - City name normalizer
  - Experience parser (string → numeric)
  - Salary normalizer (string → annual INR)
  - Skill standardizer
  - Deduplication utility
"""

import re
import hashlib
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# 1. DOMAIN KEYWORD MAP — 20 IT Domains
# ─────────────────────────────────────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    "Artificial Intelligence / Machine Learning": [
        "machine learning", "deep learning", "neural network", "nlp",
        "natural language processing", "computer vision", "ai engineer",
        "ml engineer", "llm", "generative ai", "reinforcement learning",
        "transformers", "bert", "gpt", "tensorflow", "pytorch", "keras",
        "scikit-learn", "xgboost", "lightgbm", "artificial intelligence",
    ],
    "Data Science": [
        "data scientist", "data science", "statistical modeling",
        "predictive modeling", "data mining", "r programming",
        "statistical analysis", "hypothesis testing", "regression",
        "feature engineering",
    ],
    "Data Engineering": [
        "data engineer", "data pipeline", "etl", "apache spark", "hadoop",
        "kafka", "airflow", "databricks", "snowflake", "data warehouse",
        "dbt", "bigquery", "redshift", "hive", "flink", "nifi",
        "data lakehouse", "pyspark",
    ],
    "Data Analytics": [
        "data analyst", "business analyst", "power bi", "tableau",
        "looker", "qlik", "excel", "google analytics", "bi developer",
        "reporting analyst", "dashboard", "analytics engineer",
        "data visualization",
    ],
    "Web Development": [
        "web developer", "frontend", "front-end", "backend", "back-end",
        "full stack", "fullstack", "react", "angular", "vue", "next.js",
        "node.js", "django", "flask", "html", "css", "javascript",
        "typescript", "php", "laravel", "spring boot", "asp.net",
        "ruby on rails", "graphql", "rest api",
    ],
    "Mobile App Development": [
        "mobile developer", "android developer", "ios developer",
        "flutter", "react native", "kotlin", "swift", "xamarin",
        "mobile app", "app developer",
    ],
    "DevOps": [
        "devops", "site reliability", "sre", "ci/cd", "jenkins",
        "docker", "kubernetes", "terraform", "ansible", "helm",
        "github actions", "gitlab ci", "prometheus", "grafana",
        "infrastructure as code", "iac",
    ],
    "Cloud Computing": [
        "cloud engineer", "aws", "azure", "gcp", "google cloud",
        "cloud architect", "cloud infrastructure", "lambda",
        "ec2", "s3", "cloud native", "cloud security",
        "solutions architect",
    ],
    "Cybersecurity": [
        "cybersecurity", "information security", "network security",
        "ethical hacking", "penetration testing", "pen test", "soc analyst",
        "security analyst", "vapt", "vulnerability assessment", "siem",
        "firewall", "iso 27001", "cissp", "ceh",
    ],
    "Blockchain Development": [
        "blockchain", "solidity", "smart contract", "web3", "ethereum",
        "hyperledger", "nft", "defi", "crypto", "dapp",
    ],
    "Game Development": [
        "game developer", "unity", "unreal engine", "game design",
        "c++ game", "godot", "game programmer", "3d game", "2d game",
    ],
    "QA / Software Testing": [
        "quality assurance", "qa engineer", "test engineer",
        "software testing", "automation testing", "selenium tester",
        "manual testing", "performance testing", "jmeter", "postman",
        "cypress", "appium", "test lead",
    ],
    "UI / UX Design": [
        "ui designer", "ux designer", "ui/ux", "figma", "adobe xd",
        "product designer", "interaction design", "wireframe",
        "prototyping", "user research",
    ],
    "Database Administration": [
        "database administrator", "dba", "mysql", "postgresql", "oracle dba",
        "sql server", "mongodb", "cassandra", "database management",
        "database optimization", "nosql",
    ],
    "Embedded Systems / IoT": [
        "embedded systems", "iot", "raspberry pi", "arduino",
        "rtos", "firmware", "microcontroller", "plc", "fpga",
        "embedded c", "embedded linux",
    ],
    "Network Engineering": [
        "network engineer", "ccna", "ccnp", "cisco", "routing",
        "switching", "network administrator", "wan", "lan", "vpn",
        "network infrastructure", "juniper",
    ],
    "ERP / Enterprise Systems": [
        "sap", "salesforce", "erp", "sap abap", "sap fico", "sap mm",
        "sap sd", "sap hana", "oracle erp", "dynamics 365",
        "servicenow", "sap basis",
    ],
    "Product Management": [
        "product manager", "product owner", "scrum master", "agile",
        "roadmap", "product strategy", "jira", "confluence",
        "stakeholder management", "sprint planning",
    ],
    "Technical Support / IT Operations": [
        "technical support", "it support", "helpdesk", "service desk",
        "l1 support", "l2 support", "l3 support", "it operations",
        "system administrator", "windows server", "active directory",
        "it infrastructure",
    ],
    "Software Development": [
        "software developer", "software engineer", "java developer",
        "python developer", "c# developer", "c++ developer",
        "backend developer", "api developer", "microservices",
        "software architect",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. CITY NORMALIZER
# ─────────────────────────────────────────────────────────────────────────────
CITY_ALIASES = {
    "surat": "Surat",
    "ahmedabad": "Ahmedabad",
    "ahemdabad": "Ahmedabad",
    "ahmd": "Ahmedabad",
    "vadodara": "Vadodara",
    "baroda": "Vadodara",
    "gandhinagar": "Gandhinagar",
    "gandhi nagar": "Gandhinagar",
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. SKILL ALIASES
# ─────────────────────────────────────────────────────────────────────────────
SKILL_ALIASES = {
    "reactjs": "React", "react.js": "React", "react js": "React",
    "nodejs": "Node.js", "node js": "Node.js",
    "vuejs": "Vue.js", "vue js": "Vue.js",
    "angularjs": "Angular",
    "ml": "Machine Learning", "dl": "Deep Learning",
    "ai": "Artificial Intelligence",
    "pgsql": "PostgreSQL", "postgres": "PostgreSQL",
    "mssql": "SQL Server", "k8s": "Kubernetes",
    "tf": "TensorFlow", "js": "JavaScript",
    "ts": "TypeScript", "py": "Python",
}


def classify_domain(job_title: str, skills: str) -> str:
    """Classify a job into one of 20 IT domains using keyword matching."""
    combined = f"{job_title} {skills}".lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined):
                return domain
    return "Software Development"


def normalize_city(city: str) -> str:
    """Normalize city name to canonical form."""
    if not city or not isinstance(city, str):
        return "Unknown"
    return CITY_ALIASES.get(city.strip().lower(), city.strip().title())


def parse_experience(exp_str: str) -> float:
    """Extract numeric minimum years from experience strings."""
    if not exp_str or not isinstance(exp_str, str):
        return 0.0
    text = exp_str.lower()
    if any(w in text for w in ["fresher", "0 year", "entry"]):
        return 0.0
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    return float(match.group(1)) if match else 0.0


def normalize_salary(salary_str: str) -> float:
    """Convert raw salary strings to annual INR float."""
    if not salary_str or not isinstance(salary_str, str):
        return float("nan")
    text = salary_str.lower().replace(",", "")
    if any(w in text for w in ["not disclosed", "n/a", "negotiable",
                                "competitive", "unpaid", "certificate"]):
        return float("nan")
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    if not numbers:
        return float("nan")
    values = [float(n) for n in numbers]
    avg = sum(values) / len(values)
    if "lpa" in text or "lakh" in text or "lac" in text:
        return avg * 100_000
    if "month" in text or "/m" in text:
        return avg * 12
    return avg


def generate_job_id(row: dict) -> str:
    """Create a unique fingerprint for deduplication."""
    key = f"{row.get('job_title','')}{row.get('company_name','')}{row.get('city','')}"
    return hashlib.md5(key.lower().strip().encode()).hexdigest()[:12]


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate job listings based on content fingerprint."""
    df = df.copy()
    df["_id"] = df.apply(generate_job_id, axis=1)
    before = len(df)
    df = df.drop_duplicates(subset=["_id"]).drop(columns=["_id"])
    print(f"  [dedup] Removed {before - len(df)} duplicates. Kept {len(df)} records.")
    return df


def standardize_skills(skills_str: str) -> str:
    """Normalize skill names in a comma-separated skills string."""
    if not skills_str or not isinstance(skills_str, str):
        return ""
    tokens = [s.strip() for s in skills_str.split(",")]
    return ", ".join([SKILL_ALIASES.get(t.lower(), t.strip()) for t in tokens])
