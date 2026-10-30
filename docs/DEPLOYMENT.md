# EduMetrics Deployment & Publishing Guide

## 1. Local Deployment (Windows, macOS, Linux)

### Step 1: Clone Repository
```bash
git clone https://github.com/harshthakur-45/EduMetrics.git
cd EduMetrics
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Production Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run Application
```bash
streamlit run app.py
```
The application will launch automatically at `http://localhost:8501`.

### Step 5: Execute Automated Test Suite
```bash
pytest tests/ -v
```

---

## 2. Deploying to Streamlit Community Cloud (Recommended Free Hosting)

Streamlit Community Cloud is the fastest and most seamless deployment option for EduMetrics.

### Prerequisites:
* A GitHub account with the `EduMetrics` repository pushed.
* A free account on [share.streamlit.io](https://share.streamlit.io).

### Step-by-Step Instructions:
1. Log in to [share.streamlit.io](https://share.streamlit.io) using your GitHub credentials.
2. Click the **"New app"** button.
3. In the deployment modal, specify:
   * **Repository:** `harshthakur-45/EduMetrics`
   * **Branch:** `main`
   * **Main file path:** `app.py`
   * **App URL (optional):** Custom subdomain (e.g. `edumetrics-analytics.streamlit.app`)
4. Click **"Deploy!"**.
5. Streamlit Cloud will read `requirements.txt`, install all dependencies, and deploy the application with HTTPS enabled in under 2 minutes.

---

## 3. GitHub Actions CI/CD Pipeline (Optional Automation)

You can automate test execution on every pull request by creating `.github/workflows/tests.yml`:

```yaml
name: EduMetrics CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run Pytest Suite
      run: |
        pytest tests/ -v
```
