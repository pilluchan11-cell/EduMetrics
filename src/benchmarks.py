"""
Configurable Career Benchmarks and Competency Standards for EduMetrics.
Defines role-specific skill expectation matrices, component weighting schemes,
and certification requirements for business analytics and data careers.

NOTE: These are configurable demonstration benchmarks tailored for business school
decision-science and placement evaluation, not universal industry standards.
"""

from typing import Dict, Any, List

# 5-point skill level definitions
SKILL_LEVEL_NAMES: Dict[int, str] = {
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert"
}

SKILL_NAME_TO_LEVEL: Dict[str, int] = {
    "beginner": 1,
    "basic": 2,
    "intermediate": 3,
    "advanced": 4,
    "expert": 5
}

# Standard baseline readiness component weights (Total = 1.00 / 100%)
DEFAULT_READINESS_WEIGHTS: Dict[str, float] = {
    "technical_skills": 0.40,
    "academic_performance": 0.15,
    "communication_aptitude": 0.15,
    "certifications": 0.10,
    "internship_experience": 0.10,
    "project_experience": 0.10,
}

# Human-readable labels for readiness components
COMPONENT_DISPLAY_NAMES: Dict[str, str] = {
    "technical_skills": "Technical Tool & Analytical Skills",
    "academic_performance": "Academic Performance & Aggregate Marks",
    "communication_aptitude": "Communication & Cognitive Aptitude",
    "certifications": "Industry Credentials & Certifications",
    "internship_experience": "Corporate Internship Experience",
    "project_experience": "Applied Portfolio Project Experience",
}

# Role-specific benchmarks on a 1-5 proficiency scale
CAREER_ROLE_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "Business Analyst": {
        "title": "Business Analyst",
        "description": "Bridges business stakeholders and technical engineering teams through requirements elicitation, workflow modeling, data-backed business cases, and KPI tracking.",
        "skills": {
            "Excel": 4,
            "SQL": 4,
            "Power BI": 3,
            "Python": 2,
            "Statistics": 3,
            "Communication": 5,
            "Problem-solving": 5,
            "Data Visualization": 3
        },
        "key_certifications": [
            "IBM Data Analyst Professional Certificate",
            "Microsoft Power BI Data Analyst (PL-300)",
            "IIBA Entry Certificate in Business Analysis (ECBA)",
            "Google Data Analytics Professional Certificate"
        ],
        "recommended_projects": 2,
        "sample_project_ideas": [
            "Retail customer churn and revenue attribution model in Excel and Power BI",
            "Supply chain fulfillment bottleneck analysis and process re-engineering report",
            "E-commerce conversion funnel optimization and stakeholder presentation deck"
        ]
    },
    "Data Analyst": {
        "title": "Data Analyst",
        "description": "Transforms raw transactional and operational data into executive dashboards, automated pipelines, diagnostic insights, and statistical reporting.",
        "skills": {
            "Excel": 4,
            "SQL": 5,
            "Python": 4,
            "Power BI": 4,
            "Statistics": 4,
            "Tableau": 3,
            "Communication": 4,
            "Problem-solving": 4
        },
        "key_certifications": [
            "Microsoft Power BI Data Analyst (PL-300)",
            "Google Data Analytics Professional Certificate",
            "SQL for Data Science (Coursera / HackerRank)",
            "Tableau Certified Data Analyst"
        ],
        "recommended_projects": 2,
        "sample_project_ideas": [
            "Interactive healthcare emergency admissions and staffing dashboard in Power BI",
            "Multi-million row retail sales and discount elasticity analysis using PostgreSQL and CTEs",
            "Automated financial KPI reporting pipeline in Python (Pandas) and Streamlit"
        ]
    },
    "Data Scientist": {
        "title": "Data Scientist",
        "description": "Develops mathematical formulations, statistical machine learning models, and predictive algorithms to solve complex unstructured business challenges.",
        "skills": {
            "Python": 5,
            "SQL": 4,
            "Statistics": 5,
            "Machine Learning": 5,
            "Mathematics": 5,
            "Data Visualization": 3,
            "Problem-solving": 5,
            "Communication": 3
        },
        "key_certifications": [
            "Python Data Structures & Applied Analytics",
            "Machine Learning Specialization (DeepLearning.AI / Stanford)",
            "AWS Certified Machine Learning - Specialty",
            "Google Professional Data Engineer"
        ],
        "recommended_projects": 3,
        "sample_project_ideas": [
            "Customer lifetime value (CLV) regression and random forest classification with scikit-learn",
            "Natural language processing sentiment classifier for consumer product reviews",
            "Credit risk probability of default scorecard with logistic regression and ROC-AUC validation"
        ]
    },
    "Business Intelligence Analyst": {
        "title": "Business Intelligence Analyst",
        "description": "Architects enterprise data warehouses, dimensional semantic models (star schemas), DAX measures, and corporate decision-support reporting suites.",
        "skills": {
            "Power BI": 5,
            "SQL": 5,
            "Tableau": 4,
            "Excel": 4,
            "Data Modeling / ETL": 4,
            "Statistics": 3,
            "Communication": 4,
            "Problem-solving": 4
        },
        "key_certifications": [
            "Microsoft Power BI Data Analyst (PL-300)",
            "Microsoft Certified: Azure Data Fundamentals (DP-900)",
            "SQL for Data Science",
            "Tableau Certified Desktop Specialist"
        ],
        "recommended_projects": 2,
        "sample_project_ideas": [
            "Enterprise dimensional data warehouse star schema and DAX performance tuning in Power BI",
            "Multi-source ETL data pipeline ingesting CRM and ERP data into analytical data marts",
            "Executive C-suite financial Cockpit dashboard with dynamic currency and variance parameters"
        ]
    },
    "Product Analyst": {
        "title": "Product Analyst",
        "description": "Evaluates digital user engagement, feature adoption funnels, retention cohorts, and randomized controlled A/B experiments to steer product strategy.",
        "skills": {
            "SQL": 5,
            "Statistics": 4,
            "Python": 3,
            "Excel": 4,
            "Product Metrics / A/B Testing": 4,
            "Data Visualization": 4,
            "Communication": 4,
            "Problem-solving": 5
        },
        "key_certifications": [
            "Google Data Analytics Professional Certificate",
            "SQL for Data Science",
            "Reforge Product Analytics / Amplitude Analytics Certification",
            "Python for Statistical Modeling"
        ],
        "recommended_projects": 2,
        "sample_project_ideas": [
            "Two-tailed A/B test hypothesis evaluation on onboarding funnel checkout conversion",
            "SaaS user retention cohort analysis and churn curve survival estimation in Python",
            "Feature engagement telemetry dashboard analyzing daily/monthly active users (DAU/MAU)"
        ]
    }
}

BENCHMARK_DISCLAIMER: str = (
    "These career benchmarks represent configurable demonstration standards calibrated for business analytics "
    "and management science curricula. They do not constitute universal corporate hiring criteria or a guarantee of employment."
)
