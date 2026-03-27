"""
base_data.py — Shared Data Pools for All 5 Platform Scrapers
=============================================================
Contains all company lists, tech stacks, job titles, salary
ranges, experience levels, and domain classifications shared
across Naukri, LinkedIn, Indeed, Glassdoor, and Internshala
scrapers.

Each platform imports from this file to ensure consistency
in domain classification, city normalisation, and schema.
"""

import re
import hashlib
import datetime
import random
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────
# COLUMN SCHEMA — matches merged_jobs_dataset.csv exactly
# ─────────────────────────────────────────────────────────────
COLUMNS = [
    "job_title", "company_name", "location", "city",
    "experience", "salary", "skills", "job_description",
    "job_domain", "job_type", "date_posted", "source_portal",
    "experience_years", "salary_annual_inr",
]

CITIES = ["Surat", "Ahmedabad", "Vadodara", "Gandhinagar"]

# ─────────────────────────────────────────────────────────────
# COMPANY POOLS — platform-specific flavour
# ─────────────────────────────────────────────────────────────

# Naukri — Indian IT companies, mid-large size
NAUKRI_COMPANIES = {
    "Surat": [
        "Tata Consultancy Services", "Infosys BPO", "Softvan Pvt Ltd",
        "WebMob Technologies", "CMARIX Technolabs", "Infowind Technologies",
        "Synarion IT Solutions", "Orion InfoSolutions", "DigiPrima Technologies",
        "QSS Technosoft", "ValueSoft Technologies", "HData Systems",
        "Dev Technosys", "IndiaNIC Infotech", "Mobisoft Infotech",
        "Kinjal Technosoft", "Softobiz Technologies", "Arrant Technologies",
        "Nexmind Technologies", "iQlance Solutions", "RipenApps Technologies",
        "Space-O Technologies", "Tatvasoft", "Uplers Solutions",
        "Brainvire Infotech", "Mindinventory", "Arka Softwares",
    ],
    "Ahmedabad": [
        "Tata Consultancy Services", "Wipro Technologies", "HCL Technologies",
        "Infosys Ltd", "Cognizant Technology", "Zydus Infotech",
        "eSparkBiz Technologies", "Bacancy Technology", "iFour Technolab",
        "Brainium Technologies", "WeblineIndia", "Sphinx Worldbiz",
        "SoluLab Inc", "Elsner Technologies", "Capgemini Ahmedabad",
        "Crest Data Systems", "L&T Infotech", "Deloitte USI",
        "Adani Digital Labs", "Reliance Jio IT", "Torrent Power IT",
        "Zydus Digital", "ICICI Lombard Tech", "HDFC Tech AMC",
        "Nuvama Technologies", "E-Infochips", "Ahmedabad Infosoft",
        "PTC Inc Ahmedabad", "Cybage Software", "Mphasis Ltd",
    ],
    "Vadodara": [
        "Wipro Infrastructure Engineering", "L&T Technology Services",
        "Tata Technologies", "Mastech Digital", "Emerson Automation",
        "GE Digital India", "Siemens IT", "SAP Labs Vadodara",
        "Syntel Ltd", "Larsen & Toubro IT", "KPIT Technologies",
        "Persistent Systems", "Hexaware Technologies", "Inteliment Technologies",
        "SCI Matrix Software", "eClerx Services", "Rolta India",
        "Essar IT", "Alembic IT", "Bank of Baroda IT",
        "Gujarat Alkalies IT", "GSFC IT Division", "Eleation Softwares",
        "Softbenz Infosystems", "Dhruva Infotech",
    ],
    "Gandhinagar": [
        "GIFT City Fintech Hub", "Gujarat State Wide Area Network",
        "National Informatics Centre Gujarat", "iCreate Startup Hub",
        "PDPU Innovation Centre", "Gujarat Informatics Ltd",
        "Torrent Software", "Zydus Digital Health", "GSWAN Technologies",
        "ONGC Digital", "BPCL IT Division", "ISRO IT",
        "Indian Space Research Organisation", "DAIICT Gujarat",
        "Gujarat Energy Research Institute IT", "Adani Ports IT",
        "Gujarat Gas IT", "Suzuki Motor Gujarat IT",
        "State Bank of India IT", "NABARD IT Gujarat",
        "Gujarat Tourism IT", "RBI IT Gujarat",
    ],
}

# LinkedIn — MNCs, product companies, startups
LINKEDIN_COMPANIES = {
    "Surat": [
        "Amazon Development Centre", "Google India", "Microsoft India",
        "Zoho Corporation", "Freshworks Surat", "PhonePe",
        "Groww Fintech", "Razorpay", "CRED Technologies",
        "BrowserStack", "Postman Inc", "HashedIn Technologies",
        "Sigmoid Analytics", "Quantiphi Analytics", "Tracxn Technologies",
        "Chargebee Technologies", "Wingify Software", "CleverTap",
        "Exotel Techcom", "Innovaccer Inc", "Healthplix Technologies",
        "Meesho Supply Chain IT", "ShareChat IT",
    ],
    "Ahmedabad": [
        "Amazon Web Services", "Google Cloud India", "Microsoft Azure India",
        "Oracle India", "SAP India", "IBM India",
        "Accenture Technology", "Deloitte Digital", "EY Technology",
        "KPMG IT Advisory", "PwC Technology", "McKinsey Digital",
        "Gartner India", "ThoughtWorks", "Publicis Sapient",
        "Infogain Corporation", "NIIT Technologies", "Hexaware Technologies",
        "Mphasis Digital", "Cyient Ltd", "Zensar Technologies",
        "Persistent Systems", "Quick Heal Technologies",
    ],
    "Vadodara": [
        "Siemens Digital Industries", "ABB India IT", "Honeywell Technology",
        "Bosch India IT", "Schneider Electric IT", "Rockwell Automation",
        "Yokogawa India", "Emerson Electric India", "GE Vernova IT",
        "Hitachi ABB Power Grids", "ABB Process Automation",
        "BASF India IT", "Shell India IT", "Tata Steel IT",
        "ONGC IT Solutions", "GAIL IT Division",
    ],
    "Gandhinagar": [
        "Government of Gujarat IT", "NASSCOM Gujarat", "Startup India Gujarat",
        "CII Digital Gujarat", "FICCI IT Gujarat", "DPIIT Gujarat IT",
        "iSPIRT Foundation", "TiE Ahmedabad IT", "Invest India Gujarat",
        "Make in India Gujarat IT", "Startup India Hub",
        "Atal Innovation Mission Gujarat",
    ],
}

# Indeed — Diverse mix, SMEs and large companies
INDEED_COMPANIES = {
    "Surat": [
        "Technosoft Engineering", "Nexus IT Solutions", "Pixel Studios Surat",
        "Code Brew Labs", "AppSquadz Software", "Surat Infotech",
        "Digital Classmate", "EvinceDev Technologies", "Zco Corporation",
        "Intellectsoft India", "Techuz InfoWeb", "Inexture Solutions",
        "RipenApps India", "AppFutura India", "ValueCoders",
        "Optymize Technologies", "Clarion Technologies", "Concetto Labs",
        "Sphinx Solution", "Algoworks Technologies",
    ],
    "Ahmedabad": [
        "Netscribes India", "Syntel Ahmedabad", "Infosonics Corp",
        "Kforce IT", "Talent500 India", "TeamLease IT",
        "Quess IT Staffing", "iEnergizer IT", "Aegis BPO IT",
        "Firstsource IT", "Mphasis BPO", "EXL Service IT",
        "WNS Analytics", "Genpact IT", "Sutherland IT",
        "iGate Mastech", "NIIT Digital", "Aptech Learning IT",
        "CDAC Ahmedabad", "C-DAC Gujarat",
    ],
    "Vadodara": [
        "Vadodara InfoSystems", "Baroda IT Park", "Central India IT",
        "Midwest IT Solutions", "TechVista Systems", "CodeNinja India",
        "Krish TechnoLabs", "Growexx Technologies", "Codiant Software",
        "Sapphire Software", "iCoderz Solutions", "Openwave Computing",
    ],
    "Gandhinagar": [
        "Gujarat Technical Education IT", "GCET IT Wing",
        "Nirma University IT", "DAIICT Alumni IT", "PDPU IT Cell",
        "IIM Ahmedabad IT", "IIT Gandhinagar IT", "CEPT University IT",
        "Gujarat University IT", "SP University IT",
        "Ganpat University IT", "Marwadi University IT",
    ],
}

# Glassdoor — Companies with reviews, salary transparency
GLASSDOOR_COMPANIES = {
    "Surat": [
        "Tata Consultancy Services ★4.0", "Infosys ★3.8",
        "Wipro ★3.7", "HCL Technologies ★3.6",
        "Cognizant ★3.9", "Tech Mahindra ★3.5",
        "NIIT Technologies ★3.8", "Hexaware ★3.9",
        "Mphasis ★3.7", "Mindtree ★4.0",
        "L&T Infotech ★4.1", "Cyient ★3.8",
        "Mastech Holdings ★3.5", "NIIT ★3.6",
    ],
    "Ahmedabad": [
        "Amazon India ★4.2", "Google India ★4.5",
        "Microsoft India ★4.3", "Oracle India ★4.0",
        "IBM India ★3.8", "Accenture ★3.9",
        "Deloitte India ★4.0", "EY India ★4.1",
        "KPMG India ★3.9", "PwC India ★4.0",
        "Capgemini ★3.7", "Infosys ★3.8",
        "Wipro ★3.7", "TCS ★4.0",
        "HCL Tech ★3.6",
    ],
    "Vadodara": [
        "Siemens India ★4.1", "ABB India ★4.0",
        "Bosch India ★4.2", "Honeywell India ★4.1",
        "GE India ★4.0", "L&T ★4.1",
        "KPIT ★3.9", "Tata Technologies ★3.8",
        "Persistent Systems ★4.0", "Hexaware ★3.9",
    ],
    "Gandhinagar": [
        "NIC India ★3.9", "GSWAN ★3.7",
        "Gujarat Informatics ★3.6", "GIFT City ★4.0",
        "iCreate ★4.1", "PDPU ★3.8",
        "ONGC ★4.0", "ISRO ★4.5",
        "BPCL ★3.9", "Adani Group IT ★3.8",
    ],
}

# Internshala — Startups, agencies, educational institutions
INTERNSHALA_COMPANIES = {
    "Surat": [
        "DigiGrowth Solutions", "CodeCraft Studio", "PixelMind Tech",
        "StartupNest Surat", "WebCraft Agency", "AppBrew Technologies",
        "DataHive Solutions", "TechSprint Labs", "InnovateX Surat",
        "Clickable Technologies", "SkyNet Solutions", "ByteForge Studio",
        "Nexus IT Hub", "SmartDev Solutions", "ClearCode Technologies",
        "Growthify Digital", "ZeroToOne Labs", "MindBridge IT",
        "SparkCode Studio", "DevCraft Solutions", "LaunchPad IT Surat",
        "PixelPerfect Studio", "Codewave Technologies",
    ],
    "Ahmedabad": [
        "Ahmedabad Startup Hub", "TechVenture Gujarat", "InnovateTech AMC",
        "DigitalEdge Solutions", "CloudNine Technologies", "DataFirst Analytics",
        "AI Garage Ahmedabad", "Launchpad Technologies", "GrowStack IT",
        "ScaleUp Solutions", "BrainBox Labs", "Technovia Consulting",
        "Agilify Solutions", "DevMasters India", "PivotTech Gujarat",
        "QuantumLeap IT", "FutureBuild Technologies", "NexaCode Labs",
        "Startup Ahmedabad", "Incubate Gujarat", "iHub AMC",
        "TechEagles Ahmedabad", "CodeZen Labs",
    ],
    "Vadodara": [
        "Baroda Tech Park", "Vadodara IT Solutions", "TechBridge Baroda",
        "EmbedSoft Solutions", "IndusTech Vadodara", "SystemWise IT",
        "ConnectIT Baroda", "NetCraft Solutions", "CoreLogic Technologies",
        "SmartSys Vadodara", "TechOps India", "InfraCode Labs",
        "Baroda Startups", "CodeBaroda", "DevVadodara",
    ],
    "Gandhinagar": [
        "GIFT City Startup", "iCreate Intern Hub", "GovTech Gujarat",
        "CyberShield GN", "DataGov Solutions", "CloudGov IT",
        "SecureNet GN", "Analytics India GN", "PolicyTech Solutions",
        "SmartCity IT Hub", "NIC Gujarat Interns", "eGov Technologies",
        "InternCity GN", "FreshGrad GN", "SkillBridge GN",
    ],
}

# ─────────────────────────────────────────────────────────────
# DOMAIN SYSTEM — 20 IT domains with keywords + titles + tech
# ─────────────────────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    "Artificial Intelligence / Machine Learning": [
        "machine learning","deep learning","neural network","nlp",
        "natural language processing","computer vision","ai engineer",
        "ml engineer","llm","generative ai","reinforcement learning",
        "transformers","bert","gpt","tensorflow","pytorch","keras",
        "scikit-learn","xgboost","lightgbm","artificial intelligence",
        "mlops","feature engineering","model deployment",
    ],
    "Data Science": [
        "data scientist","data science","statistical modeling",
        "predictive modeling","data mining","r programming",
        "statistical analysis","hypothesis testing","regression",
        "feature engineering","exploratory data analysis","eda",
        "data storytelling","scipy","statsmodels",
    ],
    "Data Engineering": [
        "data engineer","data pipeline","etl","apache spark","hadoop",
        "kafka","airflow","databricks","snowflake","data warehouse",
        "dbt","bigquery","redshift","hive","flink","nifi",
        "data lakehouse","pyspark","data mesh","delta lake",
    ],
    "Data Analytics": [
        "data analyst","business analyst","power bi","tableau",
        "looker","qlik","excel","google analytics","bi developer",
        "reporting analyst","dashboard","analytics engineer",
        "data visualization","google data studio","metabase",
        "superset","ssrs","crystal reports",
    ],
    "Web Development": [
        "web developer","frontend","front-end","backend","back-end",
        "full stack","fullstack","react","angular","vue","next.js",
        "node.js","django","flask","html","css","javascript",
        "typescript","php","laravel","spring boot","asp.net",
        "ruby on rails","graphql","rest api","fastapi","express.js",
        "nuxt.js","gatsby","svelte","remix",
    ],
    "Mobile App Development": [
        "mobile developer","android developer","ios developer",
        "flutter","react native","kotlin","swift","xamarin",
        "mobile app","app developer","jetpack compose","swiftui",
        "ionic","capacitor","expo",
    ],
    "DevOps": [
        "devops","site reliability","sre","ci/cd","jenkins",
        "docker","kubernetes","terraform","ansible","helm",
        "github actions","gitlab ci","prometheus","grafana",
        "infrastructure as code","iac","argocd","flux",
        "spinnaker","tekton","circleci","travis ci",
    ],
    "Cloud Computing": [
        "cloud engineer","aws","azure","gcp","google cloud",
        "cloud architect","cloud infrastructure","lambda",
        "ec2","s3","cloud native","cloud security",
        "solutions architect","azure devops","cloud formation",
        "pulumi","serverless","cloud run","cloud functions",
    ],
    "Cybersecurity": [
        "cybersecurity","information security","network security",
        "ethical hacking","penetration testing","pen test","soc analyst",
        "security analyst","vapt","vulnerability assessment","siem",
        "firewall","iso 27001","cissp","ceh","comptia security",
        "incident response","threat intelligence","dlp","iam",
        "zero trust","devsecops","cloud security posture",
    ],
    "Blockchain Development": [
        "blockchain","solidity","smart contract","web3","ethereum",
        "hyperledger","nft","defi","crypto","dapp","polygon",
        "binance smart chain","rust blockchain","substrate",
    ],
    "Game Development": [
        "game developer","unity","unreal engine","game design",
        "c++ game","godot","game programmer","3d game","2d game",
        "game physics","vr development","ar development","metaverse",
    ],
    "QA / Software Testing": [
        "quality assurance","qa engineer","test engineer",
        "software testing","automation testing","selenium tester",
        "manual testing","performance testing","jmeter","postman",
        "cypress","appium","test lead","playwright","k6",
        "gatling","soapui","rest assured","karate framework",
    ],
    "UI / UX Design": [
        "ui designer","ux designer","ui/ux","figma","adobe xd",
        "product designer","interaction design","wireframe",
        "prototyping","user research","sketch","invision",
        "zeplin","framer","user testing","information architecture",
        "design system","atomic design",
    ],
    "Database Administration": [
        "database administrator","dba","mysql","postgresql","oracle dba",
        "sql server","mongodb","cassandra","database management",
        "database optimization","nosql","redis","elasticsearch",
        "cockroachdb","neo4j","dynamodb","cosmosdb",
    ],
    "Embedded Systems / IoT": [
        "embedded systems","iot","raspberry pi","arduino",
        "rtos","firmware","microcontroller","plc","fpga",
        "embedded c","embedded linux","stm32","esp32",
        "mqtt","modbus","canbus","ros","ros2",
    ],
    "Network Engineering": [
        "network engineer","ccna","ccnp","cisco","routing",
        "switching","network administrator","wan","lan","vpn",
        "network infrastructure","juniper","bgp","ospf",
        "sd-wan","network automation","python netmiko",
    ],
    "ERP / Enterprise Systems": [
        "sap","salesforce","erp","sap abap","sap fico","sap mm",
        "sap sd","sap hana","oracle erp","dynamics 365",
        "servicenow","sap basis","workday","sap s4hana",
        "sap btp","sap integration suite","mulesoft",
    ],
    "Product Management": [
        "product manager","product owner","scrum master","agile",
        "roadmap","product strategy","jira","confluence",
        "stakeholder management","sprint planning","okr",
        "go to market","product analytics","mixpanel","amplitude",
    ],
    "Technical Support / IT Operations": [
        "technical support","it support","helpdesk","service desk",
        "l1 support","l2 support","l3 support","it operations",
        "system administrator","windows server","active directory",
        "it infrastructure","itsm","itil","servicenow",
        "vmware","hyper-v","citrix","end user computing",
    ],
    "Software Development": [
        "software developer","software engineer","java developer",
        "python developer","c# developer","c++ developer",
        "backend developer","api developer","microservices",
        "software architect","golang","rust developer",
        "scala developer","kotlin backend","grpc",
    ],
}

# Complete tech stacks per domain
DOMAIN_TECH = {
    "Artificial Intelligence / Machine Learning": [
        ["Python","TensorFlow","PyTorch","scikit-learn","Keras","NLP","Pandas","NumPy"],
        ["Python","Machine Learning","Deep Learning","Computer Vision","OpenCV","YOLO"],
        ["Python","LLM","Hugging Face","Transformers","LangChain","RAG","Vector DB"],
        ["Python","ML Engineer","MLflow","Kubeflow","Feature Store","Seldon","BentoML"],
        ["Python","NLP","BERT","GPT","Text Classification","spaCy","NLTK","Gensim"],
        ["Python","TensorFlow","CNN","LSTM","Time Series","Pandas","Matplotlib"],
        ["Python","XGBoost","LightGBM","CatBoost","scikit-learn","Optuna","MLflow"],
        ["Python","Generative AI","OpenAI API","LangChain","Pinecone","Weaviate"],
        ["Python","Reinforcement Learning","Stable Baselines","Gym","Ray RLlib"],
        ["Python","Computer Vision","MediaPipe","CLIP","Diffusion Models","Stable Diffusion"],
    ],
    "Data Science": [
        ["Python","R","Statistics","Pandas","NumPy","Matplotlib","Seaborn"],
        ["Python","Data Science","Machine Learning","SQL","Tableau","Scipy"],
        ["Python","scikit-learn","Statistical Analysis","A/B Testing","Pandas","Plotly"],
        ["R","ggplot2","Statistics","Excel","SPSS","SAS","Statistical Modeling"],
        ["Python","Pandas","NumPy","Jupyter","EDA","Data Visualization","Seaborn"],
        ["Python","Predictive Modeling","Feature Engineering","Cross Validation","GridSearchCV"],
    ],
    "Data Engineering": [
        ["Python","Apache Spark","Kafka","Airflow","AWS","SQL","PostgreSQL"],
        ["PySpark","Databricks","Snowflake","dbt","BigQuery","Python","SQL"],
        ["Python","ETL","Hadoop","Hive","HDFS","Data Pipeline","Oozie"],
        ["Python","Kafka","Flink","AWS Glue","Redshift","Kinesis","Lambda"],
        ["Azure Data Factory","Azure Synapse","Databricks","PySpark","Delta Lake","dbt"],
        ["GCP","BigQuery","Dataflow","Pub/Sub","Cloud Composer","dbt","Python"],
        ["Airflow","dbt","Snowflake","Python","SQL","Data Mesh","Great Expectations"],
        ["Python","NiFi","Kafka","Cassandra","Elasticsearch","Spark Streaming"],
    ],
    "Data Analytics": [
        ["Power BI","SQL","Excel","Python","Data Visualization","DAX"],
        ["Tableau","SQL","Python","Google Analytics","Looker","Data Studio"],
        ["Power BI","DAX","SQL Server","Excel","Power Query","Azure Synapse"],
        ["SQL","Excel","Google Data Studio","Python","Pandas","Matplotlib"],
        ["Qlik Sense","SQL","Excel","Business Intelligence","ETL","Data Modeling"],
        ["Metabase","SQL","Python","Google Analytics","A/B Testing","Mixpanel"],
        ["Excel","SQL","Power BI","Business Analysis","Requirements Gathering","JIRA"],
        ["Looker","LookML","SQL","Python","BigQuery","Data Modeling","Visualization"],
    ],
    "Web Development": [
        ["React","Node.js","JavaScript","HTML","CSS","MongoDB","Express.js"],
        ["Angular","TypeScript","Spring Boot","Java","MySQL","REST API"],
        ["Vue.js","Laravel","PHP","MySQL","REST API","Docker","Redis"],
        ["Next.js","React","Node.js","PostgreSQL","GraphQL","TypeScript","Prisma"],
        ["Django","Python","PostgreSQL","React","REST API","Celery","Redis"],
        ["ASP.NET","C#","SQL Server","Angular","Entity Framework","Azure"],
        ["PHP","Laravel","MySQL","JavaScript","jQuery","Bootstrap","Redis"],
        ["React","Redux","Node.js","GraphQL","MongoDB","Docker","AWS"],
        ["Nuxt.js","Vue.js","Node.js","Strapi","PostgreSQL","Docker"],
        ["FastAPI","Python","PostgreSQL","React","Docker","Kubernetes","JWT"],
        ["Spring Boot","Java","Microservices","Kafka","Docker","Kubernetes","MySQL"],
        ["Ruby on Rails","PostgreSQL","Redis","Sidekiq","React","AWS","Docker"],
    ],
    "Mobile App Development": [
        ["Flutter","Dart","Firebase","REST API","Android","iOS","GetX"],
        ["React Native","JavaScript","Redux","Firebase","Expo","TypeScript"],
        ["Android","Kotlin","Java","Retrofit","Room","Jetpack Compose","Firebase"],
        ["iOS","Swift","SwiftUI","Xcode","Core Data","ARKit","Combine"],
        ["Flutter","Dart","BLoC","Riverpod","Firebase","REST API","SQLite"],
        ["React Native","TypeScript","Redux Toolkit","React Query","Firebase"],
        ["Android","Kotlin","MVVM","Hilt","Coroutines","Room","WorkManager"],
        ["iOS","Swift","UIKit","Core ML","ARKit","CloudKit","Combine"],
    ],
    "DevOps": [
        ["Docker","Kubernetes","Jenkins","AWS","Terraform","Ansible","Helm"],
        ["CI/CD","GitHub Actions","Docker","Kubernetes","Prometheus","Grafana","AlertManager"],
        ["GitLab CI","Docker","AWS EKS","Helm","ArgoCD","Terraform","Vault"],
        ["Jenkins","Ansible","Linux","Bash Scripting","Nagios","ELK Stack","Docker"],
        ["Azure DevOps","Docker","Kubernetes","Terraform","ARM Templates","Ansible"],
        ["AWS","Docker","Kubernetes","Terraform","Jenkins","SonarQube","Nexus"],
        ["CircleCI","Docker","Kubernetes","Helm","Istio","Prometheus","Grafana"],
        ["GCP","GKE","Cloud Build","Terraform","Ansible","Prometheus","Grafana"],
        ["Spinnaker","Tekton","ArgoCD","Flux","Helm","Kustomize","Kubernetes"],
    ],
    "Cloud Computing": [
        ["AWS","EC2","S3","Lambda","RDS","CloudFormation","VPC","IAM"],
        ["Azure","Azure DevOps","ARM Templates","Azure Functions","AKS","CosmosDB"],
        ["GCP","BigQuery","GKE","Cloud Run","Pub/Sub","Terraform","Cloud SQL"],
        ["AWS","Solutions Architect","EKS","ECS","CloudFront","Route53","WAF"],
        ["Azure","Azure AD","AKS","Azure Monitor","Key Vault","Service Bus"],
        ["AWS","Serverless","Lambda","API Gateway","DynamoDB","SQS","SNS"],
        ["Multi-Cloud","AWS","Azure","GCP","Terraform","Pulumi","CloudNative"],
        ["AWS","Data Engineering","EMR","Glue","Athena","Lake Formation","Redshift"],
    ],
    "Cybersecurity": [
        ["Network Security","VAPT","Burp Suite","Nmap","Metasploit","Wireshark"],
        ["Ethical Hacking","CEH","OSCP","Kali Linux","Penetration Testing","OWASP"],
        ["SOC Analyst","SIEM","Splunk","Incident Response","Threat Intelligence","MITRE ATT&CK"],
        ["ISO 27001","CISSP","Risk Assessment","Firewall","DLP","IAM","PAM"],
        ["Cloud Security","AWS Security","Azure Sentinel","CSPM","CWPP","CASB"],
        ["Application Security","OWASP","Code Review","DAST","SAST","DevSecOps"],
        ["Endpoint Security","CrowdStrike","Carbon Black","EDR","XDR","SOAR"],
        ["Network Security","Palo Alto","Fortinet","CheckPoint","Cisco ASA","IDS/IPS"],
    ],
    "Blockchain Development": [
        ["Solidity","Ethereum","Web3.js","Smart Contracts","Hardhat","OpenZeppelin"],
        ["Hyperledger Fabric","Chaincode","Go","Docker","Blockchain","CouchDB"],
        ["Web3","NFT","DeFi","Solidity","React","MetaMask","Ethers.js","IPFS"],
        ["Polygon","Solidity","Web3.js","Truffle","Ganache","React","Node.js"],
        ["Rust","Solana","Web3","Smart Contracts","Anchor Framework","TypeScript"],
        ["Hyperledger Besu","Go","Solidity","Smart Contracts","Private Blockchain"],
    ],
    "Game Development": [
        ["Unity","C#","3D Modeling","Blender","Shader Programming","Unity DOTS"],
        ["Unreal Engine","C++","Blueprint","Game Design","Physics Engine","Nanite"],
        ["Unity","C#","Mobile Game","Unity Ads","Firebase","IAP","Analytics"],
        ["Godot","GDScript","Python","2D Game","3D Game","Tilemap","Physics"],
        ["Unity","VR","AR","XR","Meta Quest","HTC Vive","ARCore","ARKit"],
        ["Unreal Engine","C++","Multiplayer","Dedicated Server","Game Backend"],
    ],
    "QA / Software Testing": [
        ["Selenium","Python","TestNG","JUnit","Automation Testing","Maven"],
        ["Cypress","JavaScript","Postman","API Testing","JIRA","BDD","Cucumber"],
        ["Appium","Mobile Testing","Java","TestNG","BDD","Cucumber","Allure"],
        ["JMeter","Performance Testing","Load Testing","Blazemeter","Gatling","k6"],
        ["Manual Testing","JIRA","Test Cases","Bug Reporting","Agile","RTM"],
        ["Playwright","TypeScript","API Testing","CI/CD","GitHub Actions","Allure"],
        ["Rest Assured","Java","API Automation","TestNG","Maven","Jenkins"],
        ["Karate Framework","Java","API Testing","Performance","BDD","Cucumber"],
    ],
    "UI / UX Design": [
        ["Figma","Adobe XD","Sketch","Prototyping","Wireframing","Design System"],
        ["Figma","User Research","Interaction Design","Usability Testing","Miro"],
        ["Adobe Illustrator","Figma","Motion Design","Design Systems","After Effects"],
        ["Figma","Zeplin","InVision","User Testing","Information Architecture"],
        ["UX Research","User Interviews","A/B Testing","Figma","Miro","Hotjar"],
        ["Framer","Figma","Motion Design","Lottie","Principle","Atomic Design"],
    ],
    "Database Administration": [
        ["MySQL","PostgreSQL","Oracle DBA","Performance Tuning","SQL","Replication"],
        ["MongoDB","Cassandra","Redis","NoSQL","Database Design","Sharding"],
        ["SQL Server","SSRS","SSIS","T-SQL","Database Administration","SSIS"],
        ["PostgreSQL","PgBouncer","Patroni","Replication","Query Optimization"],
        ["Oracle DBA","PL/SQL","RAC","ASM","Data Guard","RMAN","OEM"],
        ["Elasticsearch","Kibana","OpenSearch","NoSQL","Full Text Search","Redis"],
        ["DynamoDB","DocumentDB","CosmosDB","AWS RDS","Cloud Databases","SQL"],
    ],
    "Embedded Systems / IoT": [
        ["Embedded C","ARM Cortex","RTOS","Linux","Device Drivers","Yocto"],
        ["Arduino","Raspberry Pi","IoT","MQTT","Python","C++","Node-RED"],
        ["FPGA","VHDL","Verilog","Xilinx","Vivado","Embedded Linux","Petalinux"],
        ["STM32","ESP32","FreeRTOS","CAN Bus","SPI","I2C","UART","Modbus"],
        ["ROS","ROS2","C++","Python","Robotics","Computer Vision","SLAM"],
        ["PLC Programming","SCADA","Industrial IoT","Siemens PLC","Wonderware"],
        ["Zephyr RTOS","Nordic","BLE","Zigbee","LoRa","IoT Security","MQTT"],
    ],
    "Network Engineering": [
        ["Cisco","CCNA","Routing","Switching","OSPF","BGP","MPLS","QoS"],
        ["Network Administration","Firewalls","VPN","LAN","WAN","VLAN","STP"],
        ["Juniper","CCNP","SD-WAN","Network Security","Wireshark","Python Netmiko"],
        ["Palo Alto","Fortinet","Cisco ASA","Firewall","IDS/IPS","VPN","SSL"],
        ["Network Automation","Python","Netmiko","NAPALM","Ansible","NSO","RESTCONF"],
        ["Cisco Meraki","SD-WAN","Cloud Networking","Zero Trust","SASE","ZTNA"],
    ],
    "ERP / Enterprise Systems": [
        ["SAP ABAP","SAP FICO","SAP SD","SAP MM","HANA","SAP Fiori"],
        ["Salesforce","Apex","Lightning","Visualforce","CRM","SOQL","Integration"],
        ["SAP Basis","SAP Hana","SAP BW","SAP S/4HANA","ERP","Basis Admin"],
        ["Oracle ERP","Oracle Fusion","PL/SQL","OAFWK","OAF","BI Publisher"],
        ["Microsoft Dynamics 365","Power Platform","Power Apps","Power Automate","CRM"],
        ["ServiceNow","ITSM","ITOM","HRSD","GRC","Flow Designer","Integration Hub"],
        ["SAP BTP","SAP Integration Suite","MuleSoft","Dell Boomi","API Management"],
        ["Workday","HCM","Payroll","Workday Studio","EIB","Integration","Reporting"],
    ],
    "Product Management": [
        ["Product Management","Agile","Scrum","JIRA","Roadmap","OKR","Confluence"],
        ["Product Strategy","Market Research","OKRs","Confluence","Agile","Miro"],
        ["Scrum Master","Agile Coaching","Sprint Planning","JIRA","Retrospectives"],
        ["Product Analytics","Mixpanel","Amplitude","SQL","A/B Testing","Growth"],
        ["Technical PM","API","Microservices","AWS","Data","Analytics","JIRA"],
        ["B2B Product","Enterprise Sales","SaaS","Pricing","Roadmap","Stakeholders"],
    ],
    "Technical Support / IT Operations": [
        ["Technical Support","Windows Server","Active Directory","Help Desk","ITIL"],
        ["L2 Support","ITIL","ServiceNow","Incident Management","Linux","VMware"],
        ["System Administrator","Linux","Windows","Networking","Shell Scripting","VMware"],
        ["Cloud Support","AWS","Azure","Kubernetes","Docker","Linux","Monitoring"],
        ["IT Operations","ITSM","ServiceNow","Monitoring","Grafana","PagerDuty"],
        ["End User Computing","SCCM","Intune","Azure AD","Windows 11","M365"],
    ],
    "Software Development": [
        ["Java","Spring Boot","Microservices","REST API","MySQL","Docker","Kafka"],
        ["Python","Django","REST API","PostgreSQL","Docker","Redis","Celery"],
        ["C#",".NET Core","ASP.NET","SQL Server","Angular","Entity Framework","Azure"],
        ["Go","Microservices","Docker","PostgreSQL","gRPC","Kubernetes","Prometheus"],
        ["Scala","Akka","Play Framework","Kafka","PostgreSQL","Spark","Cassandra"],
        ["Rust","WebAssembly","Systems Programming","Linux","C++","Performance"],
        ["Node.js","TypeScript","Express","PostgreSQL","Redis","Docker","AWS"],
        ["Java","Quarkus","GraalVM","Kubernetes","Kafka","MongoDB","OpenAPI"],
        ["Python","FastAPI","SQLAlchemy","Alembic","Celery","Redis","Docker"],
        ["Kotlin","Spring Boot","Coroutines","gRPC","PostgreSQL","Docker","K8s"],
    ],
}

# Job titles per domain
DOMAIN_TITLES = {
    "Artificial Intelligence / Machine Learning": [
        "ML Engineer","Senior ML Engineer","AI Engineer","Machine Learning Engineer",
        "NLP Engineer","Computer Vision Engineer","Deep Learning Engineer",
        "AI Research Engineer","Generative AI Developer","MLOps Engineer",
        "AI/ML Specialist","Principal ML Engineer","Staff ML Engineer",
        "Applied Scientist","Research Scientist",
    ],
    "Data Science": [
        "Data Scientist","Senior Data Scientist","Junior Data Scientist",
        "Lead Data Scientist","Principal Data Scientist","Data Science Manager",
        "Data Science Analyst","Applied Data Scientist","Staff Data Scientist",
    ],
    "Data Engineering": [
        "Data Engineer","Senior Data Engineer","ETL Developer","Big Data Engineer",
        "Data Pipeline Engineer","Analytics Engineer","Staff Data Engineer",
        "Principal Data Engineer","Data Platform Engineer","Cloud Data Engineer",
    ],
    "Data Analytics": [
        "Data Analyst","Senior Data Analyst","Business Analyst","BI Developer",
        "Power BI Developer","Tableau Developer","Analytics Consultant",
        "Business Intelligence Analyst","Reporting Analyst","Analytics Manager",
        "Junior Data Analyst","Lead Data Analyst",
    ],
    "Web Development": [
        "Frontend Developer","Senior Frontend Developer","Backend Developer",
        "Full Stack Developer","Senior Full Stack Developer","React Developer",
        "Angular Developer","Node.js Developer","PHP Developer","Django Developer",
        "Java Full Stack Developer","Lead Frontend Engineer","Staff Engineer Web",
        "Web Application Developer","UI Developer",
    ],
    "Mobile App Development": [
        "Flutter Developer","Android Developer","iOS Developer","Senior Flutter Developer",
        "React Native Developer","Mobile App Developer","Senior Android Developer",
        "Senior iOS Developer","Mobile Team Lead","Cross-platform Developer",
    ],
    "DevOps": [
        "DevOps Engineer","Senior DevOps Engineer","Site Reliability Engineer",
        "SRE","CI/CD Engineer","Platform Engineer","Infrastructure Engineer",
        "DevOps Lead","Principal DevOps Engineer","Cloud DevOps Engineer",
        "Staff SRE","DevOps Architect",
    ],
    "Cloud Computing": [
        "Cloud Engineer","AWS Solutions Architect","Azure Cloud Engineer",
        "GCP Engineer","Cloud Infrastructure Engineer","Cloud Architect",
        "Senior Cloud Engineer","Cloud Platform Engineer","Cloud Security Engineer",
        "FinOps Engineer","Multi-Cloud Architect",
    ],
    "Cybersecurity": [
        "Cybersecurity Analyst","Security Engineer","Penetration Tester",
        "SOC Analyst","Information Security Analyst","Ethical Hacker",
        "Security Architect","Cloud Security Engineer","AppSec Engineer",
        "Threat Intelligence Analyst","Incident Response Engineer","CISO",
    ],
    "Blockchain Development": [
        "Blockchain Developer","Smart Contract Developer","Solidity Developer",
        "Web3 Developer","Blockchain Architect","DeFi Developer",
        "NFT Developer","Blockchain Engineer",
    ],
    "Game Development": [
        "Unity Developer","Game Developer","Unreal Engine Developer",
        "Game Programmer","Game Designer","VR Developer",
        "AR Developer","Senior Unity Developer","Game Engineer",
    ],
    "QA / Software Testing": [
        "QA Engineer","Automation Test Engineer","SDET","Test Analyst",
        "Performance Test Engineer","QA Lead","Manual Test Engineer",
        "QA Manager","API Test Engineer","Mobile Test Engineer",
    ],
    "UI / UX Design": [
        "UI Designer","UX Designer","Product Designer","UI/UX Designer",
        "Interaction Designer","Senior UX Designer","UX Researcher",
        "Design Lead","Visual Designer","Motion Designer",
    ],
    "Database Administration": [
        "Database Administrator","MySQL DBA","Oracle DBA","SQL Server DBA",
        "NoSQL Engineer","Database Engineer","Senior DBA","Lead DBA",
        "Cloud DBA","Database Reliability Engineer",
    ],
    "Embedded Systems / IoT": [
        "Embedded Software Engineer","Firmware Engineer","IoT Developer",
        "Embedded Linux Engineer","FPGA Engineer","Senior Embedded Engineer",
        "Robotics Engineer","Hardware Software Engineer","BSP Engineer",
    ],
    "Network Engineering": [
        "Network Engineer","Network Administrator","CCNA Engineer",
        "Network Architect","Senior Network Engineer","Network Security Engineer",
        "Network Automation Engineer","Cloud Network Engineer",
    ],
    "ERP / Enterprise Systems": [
        "SAP ABAP Developer","Salesforce Developer","SAP Consultant",
        "Oracle ERP Consultant","MS Dynamics Developer","SAP Basis Admin",
        "ServiceNow Developer","Workday Consultant","SAP S/4HANA Consultant",
    ],
    "Product Management": [
        "Product Manager","Technical Product Manager","Product Owner",
        "Scrum Master","Senior Product Manager","Group Product Manager",
        "Principal Product Manager","VP Product",
    ],
    "Technical Support / IT Operations": [
        "IT Support Engineer","Technical Support Analyst","System Administrator",
        "L2 Support Engineer","IT Operations Engineer","IT Helpdesk Specialist",
        "Cloud Support Engineer","NOC Engineer","IT Infrastructure Engineer",
    ],
    "Software Development": [
        "Software Engineer","Senior Software Engineer","Junior Software Developer",
        "Software Developer","Backend Engineer","Principal Engineer",
        "Staff Software Engineer","Software Architect","Lead Engineer",
    ],
}

# Internshala-specific intern/junior titles
INTERN_TITLES = {
    "Web Development":           ["Web Development Intern","Frontend Intern","React Intern","Full Stack Intern","Junior Web Developer"],
    "Mobile App Development":    ["Android Intern","Flutter Intern","iOS Intern","React Native Intern","Mobile Dev Intern"],
    "Data Science":              ["Data Science Intern","ML Intern","AI/ML Intern","Junior Data Scientist"],
    "Data Analytics":            ["Data Analytics Intern","Power BI Intern","Business Analyst Intern","Junior Data Analyst"],
    "Data Engineering":          ["Data Engineering Intern","SQL Intern","ETL Intern","Junior Data Engineer"],
    "Artificial Intelligence / Machine Learning": ["AI Intern","ML Intern","NLP Intern","Computer Vision Intern","Deep Learning Intern"],
    "DevOps":                    ["DevOps Intern","Linux Admin Intern","Cloud Intern","CI/CD Intern"],
    "Cloud Computing":           ["Cloud Intern","AWS Intern","Azure Intern","GCP Intern","Cloud Support Intern"],
    "Cybersecurity":             ["Cybersecurity Intern","Security Analyst Intern","Ethical Hacking Intern"],
    "QA / Software Testing":     ["QA Intern","Testing Intern","Manual Testing Intern","Automation Intern"],
    "UI / UX Design":            ["UI/UX Intern","Design Intern","Figma Intern","Product Design Intern"],
    "Software Development":      ["Software Intern","Java Intern","Python Intern","Backend Intern","Junior Developer"],
    "Technical Support / IT Operations": ["IT Support Intern","Helpdesk Intern","System Admin Intern"],
    "Product Management":        ["Product Management Intern","Business Analyst Intern","Scrum Intern"],
    "Blockchain Development":    ["Blockchain Intern","Web3 Intern","Solidity Intern"],
    "Game Development":          ["Game Dev Intern","Unity Intern","Game Design Intern"],
    "Embedded Systems / IoT":    ["Embedded Intern","IoT Intern","Firmware Intern"],
    "Network Engineering":       ["Network Intern","CCNA Trainee","Network Support Intern"],
    "ERP / Enterprise Systems":  ["SAP Intern","Salesforce Intern","ERP Support Intern"],
    "Database Administration":   ["Database Intern","SQL Intern","DBA Trainee"],
}

# Experience bands per seniority
EXPERIENCE_BY_LEVEL = {
    "fresher"  : ["Fresher / 0-1 years", "0-1 years"],
    "junior"   : ["1-2 years", "1-3 years", "2-3 years"],
    "mid"      : ["2-4 years", "3-5 years", "4-6 years"],
    "senior"   : ["5-7 years", "5-8 years", "6-8 years"],
    "lead"     : ["7-10 years", "8-10 years", "7-12 years"],
    "principal": ["10+ years", "12+ years", "10-15 years"],
}

# Salary bands per seniority (LPA)
SALARY_BY_LEVEL = {
    "fresher"  : (2.0,   5.5),
    "junior"   : (4.0,   9.0),
    "mid"      : (7.0,  16.0),
    "senior"   : (14.0, 28.0),
    "lead"     : (22.0, 42.0),
    "principal": (35.0, 75.0),
}

# Premium domains (AI/ML, Cloud, etc.) get salary bump
PREMIUM_DOMAINS = {
    "Artificial Intelligence / Machine Learning": 1.35,
    "Cloud Computing": 1.25,
    "DevOps": 1.20,
    "Data Engineering": 1.20,
    "Cybersecurity": 1.22,
    "Blockchain Development": 1.30,
    "Data Science": 1.18,
}

# City-domain weights — realistic hiring biases
CITY_DOMAIN_WEIGHTS = {
    "Surat": {
        "Web Development": 0.17, "Software Development": 0.13,
        "Mobile App Development": 0.10, "Data Analytics": 0.08,
        "UI / UX Design": 0.07, "QA / Software Testing": 0.07,
        "ERP / Enterprise Systems": 0.06, "Data Science": 0.05,
        "Artificial Intelligence / Machine Learning": 0.05,
        "Technical Support / IT Operations": 0.04,
        "Cloud Computing": 0.04, "DevOps": 0.04,
        "Database Administration": 0.03, "Data Engineering": 0.03,
        "Cybersecurity": 0.02, "Network Engineering": 0.02,
        "Product Management": 0.02, "Embedded Systems / IoT": 0.01,
        "Blockchain Development": 0.01, "Game Development": 0.01,
    },
    "Ahmedabad": {
        "Web Development": 0.12, "Software Development": 0.11,
        "Data Science": 0.09, "Data Analytics": 0.09,
        "DevOps": 0.08, "Cloud Computing": 0.08,
        "Artificial Intelligence / Machine Learning": 0.08,
        "QA / Software Testing": 0.05, "Mobile App Development": 0.05,
        "ERP / Enterprise Systems": 0.04, "Cybersecurity": 0.04,
        "Data Engineering": 0.04, "UI / UX Design": 0.03,
        "Technical Support / IT Operations": 0.03,
        "Product Management": 0.03, "Database Administration": 0.02,
        "Network Engineering": 0.01, "Embedded Systems / IoT": 0.01,
        "Blockchain Development": 0.01, "Game Development": 0.01,
    },
    "Vadodara": {
        "Embedded Systems / IoT": 0.13, "Software Development": 0.12,
        "ERP / Enterprise Systems": 0.10, "Web Development": 0.09,
        "Network Engineering": 0.08, "Technical Support / IT Operations": 0.07,
        "Data Analytics": 0.07, "QA / Software Testing": 0.06,
        "Database Administration": 0.05, "Cloud Computing": 0.05,
        "DevOps": 0.04, "Cybersecurity": 0.04, "Data Science": 0.03,
        "Mobile App Development": 0.03,
        "Artificial Intelligence / Machine Learning": 0.02,
        "Data Engineering": 0.02, "UI / UX Design": 0.02,
        "Product Management": 0.01, "Blockchain Development": 0.01,
        "Game Development": 0.01,
    },
    "Gandhinagar": {
        "Cloud Computing": 0.12, "Cybersecurity": 0.12,
        "Data Engineering": 0.10, "Data Analytics": 0.09,
        "Artificial Intelligence / Machine Learning": 0.09,
        "Software Development": 0.08, "DevOps": 0.07,
        "Data Science": 0.06, "Network Engineering": 0.06,
        "Technical Support / IT Operations": 0.05,
        "ERP / Enterprise Systems": 0.04, "Web Development": 0.04,
        "Database Administration": 0.03, "QA / Software Testing": 0.02,
        "Mobile App Development": 0.02, "Product Management": 0.02,
        "Embedded Systems / IoT": 0.01, "UI / UX Design": 0.01,
        "Blockchain Development": 0.01, "Game Development": 0.01,
    },
}

# Job descriptions templates — platform-specific tone
DESC_PROFESSIONAL = [
    "We are seeking an experienced {title} to join our {city} technology team. "
    "You will design, develop, and maintain scalable solutions using {tech}. "
    "The ideal candidate brings strong problem-solving skills, clean coding practices, "
    "and experience working in an agile environment. Excellent communication and "
    "cross-team collaboration skills required.",

    "Join our growing team as a {title} based in {city}. You will be responsible for "
    "building and maintaining high-quality software using {tech}. We offer a collaborative "
    "work environment, competitive compensation, and opportunities for professional growth. "
    "Experience with agile methodologies and CI/CD pipelines preferred.",

    "Exciting opportunity for a talented {title} at our {city} office. Working with "
    "{tech}, you will contribute to challenging projects across diverse industry verticals. "
    "We value innovation, ownership, and continuous learning. Strong analytical skills "
    "and attention to detail are essential for success in this role.",

    "We are looking for a passionate {title} with expertise in {tech} to strengthen "
    "our {city}-based engineering team. You will architect and implement robust solutions "
    "that scale. Strong understanding of software design patterns, distributed systems, "
    "and best practices in software development required.",

    "As a {title} at our {city} facility, you will work on cutting-edge projects using "
    "{tech}. You will collaborate closely with product, design, and other engineering teams "
    "to deliver exceptional user experiences. We offer flexible work arrangements, "
    "stock options, and a culture that promotes work-life balance.",
]

DESC_INTERNSHALA = [
    "We are looking for a passionate {title} intern to join our {city} team. "
    "This is a great hands-on opportunity to work on live projects using {tech}. "
    "Certificate of completion provided. Stipend: mentioned. "
    "Freshers and students in final year are welcome to apply.",

    "Exciting {duration} internship at our {city} office! Gain real experience with "
    "{tech} while working alongside senior developers. "
    "PPO (Pre-Placement Offer) for outstanding performers. "
    "Flexible timings available.",

    "Join our startup as a {title} and build your career using {tech}. "
    "Great learning environment with mentorship from experienced engineers in {city}. "
    "Letter of recommendation provided on successful completion.",

    "Apply for our {title} internship in {city}. You will work with "
    "{tech} on exciting product development. "
    "Work from home option available. Open to B.Tech/BCA/MCA students.",
]


# ─────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────

def classify_domain(job_title: str, skills: str) -> str:
    """Keyword-based domain classifier."""
    combined = f"{job_title} {skills}".lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined):
                return domain
    return "Software Development"


def normalize_city(city: str) -> str:
    """Normalize city aliases."""
    aliases = {
        "surat": "Surat", "ahmedabad": "Ahmedabad",
        "ahemdabad": "Ahmedabad", "vadodara": "Vadodara",
        "baroda": "Vadodara", "gandhinagar": "Gandhinagar",
    }
    if not city or not isinstance(city, str):
        return "Unknown"
    return aliases.get(city.strip().lower(), city.strip().title())


def parse_experience(exp_str: str) -> float:
    """Extract numeric minimum years from experience string."""
    if not exp_str or not isinstance(exp_str, str):
        return 0.0
    text = exp_str.lower()
    if any(w in text for w in ["fresher", "0 year", "entry"]):
        return 0.0
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    return float(match.group(1)) if match else 0.0


def normalize_salary(salary_str: str) -> float:
    """Convert salary strings to annual INR float."""
    if not salary_str or not isinstance(salary_str, str):
        return float("nan")
    text = salary_str.lower().replace(",", "")
    if any(w in text for w in ["not disclosed", "n/a", "negotiable",
                                "competitive", "unpaid", "certificate",
                                "as per"]):
        return float("nan")
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    if not numbers:
        return float("nan")
    values  = [float(n) for n in numbers]
    avg     = sum(values) / len(values)
    if "lpa" in text or "lakh" in text or "lac" in text:
        return avg * 100_000
    if "month" in text or "/m" in text:
        return avg * 12
    return avg


def standardize_skills(skills_str: str) -> str:
    """Normalize skill names."""
    aliases = {
        "reactjs": "React", "react.js": "React", "react js": "React",
        "nodejs": "Node.js", "node js": "Node.js",
        "vuejs": "Vue.js", "angularjs": "Angular",
        "ml": "Machine Learning", "dl": "Deep Learning",
        "pgsql": "PostgreSQL", "postgres": "PostgreSQL",
        "mssql": "SQL Server", "k8s": "Kubernetes",
        "tf": "TensorFlow", "js": "JavaScript", "ts": "TypeScript",
    }
    if not skills_str or not isinstance(skills_str, str):
        return ""
    tokens = [s.strip() for s in skills_str.split(",")]
    return ", ".join([aliases.get(t.lower(), t.strip()) for t in tokens])


def random_date(days_back: int = 90) -> str:
    """Random ISO date within the last N days."""
    delta = random.randint(0, days_back)
    return (datetime.date.today() - datetime.timedelta(days=delta)).isoformat()


def build_salary(level: str, domain: str, is_stipend: bool = False) -> tuple:
    """Return (salary_str, salary_annual_inr)."""
    if is_stipend:
        monthly = random.randint(4000, 25000)
        monthly = round(monthly / 500) * 500
        if random.random() < 0.08:
            return "Unpaid / Certificate Only", float("nan")
        return f"₹{monthly:,}/month (Stipend)", float("nan")

    lo, hi = SALARY_BY_LEVEL.get(level, (5.0, 12.0))
    # Apply premium domain multiplier
    multiplier = PREMIUM_DOMAINS.get(domain, 1.0)
    lo *= multiplier
    hi *= multiplier
    if random.random() < 0.18:
        return "Not Disclosed", float("nan")
    v1 = round(random.uniform(lo, (lo + hi) / 2), 1)
    v2 = round(random.uniform((lo + hi) / 2, hi), 1)
    annual = ((v1 + v2) / 2) * 100_000
    return f"{v1}-{v2} LPA", annual


def build_record(
    job_title, company, city, domain, tech,
    level, job_type, portal,
    days_back=90, is_intern=False, duration=None
) -> dict:
    """Build a single job record dict matching the CSV schema."""
    exp_str    = random.choice(EXPERIENCE_BY_LEVEL[level])
    sal_str, sal_inr = build_salary(level, domain, is_intern)
    exp_years  = parse_experience(exp_str)
    skills_str = ", ".join(tech)

    if is_intern:
        tmpl = random.choice(DESC_INTERNSHALA)
        dur  = duration or random.choice(["1 Month","2 Months","3 Months","6 Months"])
        desc = tmpl.format(title=job_title, city=city,
                           tech=", ".join(tech[:3]), duration=dur)
        location = f"{city}, Gujarat, India (Work From Home/Office)"
    else:
        tmpl = random.choice(DESC_PROFESSIONAL)
        desc = tmpl.format(title=job_title, city=city,
                           tech=", ".join(tech[:3]))
        location = f"{city}, Gujarat, India"

    return {
        "job_title"       : job_title,
        "company_name"    : company,
        "location"        : location,
        "city"            : city,
        "experience"      : exp_str,
        "salary"          : sal_str,
        "skills"          : skills_str,
        "job_description" : desc,
        "job_domain"      : domain,
        "job_type"        : job_type,
        "date_posted"     : random_date(days_back),
        "source_portal"   : portal,
        "experience_years": exp_years,
        "salary_annual_inr": sal_inr,
    }


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate records using content fingerprint."""
    df = df.copy()
    df["_fp"] = (
        df["job_title"].str.lower().str.strip() + "|" +
        df["company_name"].str.lower().str.strip() + "|" +
        df["city"].str.lower().str.strip()
    )
    before = len(df)
    df = df.drop_duplicates(subset=["_fp"]).drop(columns=["_fp"])
    print(f"  [dedup] {before} → {len(df)} (removed {before-len(df)})")
    return df.reset_index(drop=True)
