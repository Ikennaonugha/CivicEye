# 👁️ CivicEye

> **Transparent, Central Auditing & Civic Infrastructure Monitoring for Lagos State.**

CivicEye is an open civic-technology platform designed to foster transparency, public accountability, and citizen oversight across public procurement and infrastructure projects in Lagos State. 

By ingesting open procurement records structured under the **Open Contracting Data Standard (OCDS)** and pairing them with real-time community oversight, CivicEye enables residents, Civil Society Organizations (CSOs), and journalists to track project budgets, verify physical site progress, submit geotagged photo reports ("civic flags"), and stay updated on governance news.

---

## ✨ Key Features

* **LGA Project Tracking:** Filter, search, and monitor public infrastructure contracts across all 20 Local Government Areas (LGAs) in Lagos State.
* **Civic Flagging & Auditing:** Citizens can report project delays, substandard execution, or contract issues with verified site photos and automatic GPS coordinates.
* **OCDS Open Contracting Integration:** Ingests official procurement data (budgets, procuring entities, award dates, and contractors) in standardized OCDS JSON formats.
* **Automated Government News Feed:** Safely ingests and categorizes governance, economy, tech, and society news from leading Nigerian media outlets.
* **Analytical Dashboard:** Real-time visibility into state capital expenditure, project completion rates, and citizen flagging trends.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10+, Django 5.0+ / 6.0+
* **Database:** PostgreSQL (Hosted on Supabase with Transaction Pooling via pgBouncer)
* **Frontend:** HTML5, Bootstrap 5, Modern SCSS (Compiled via Dart Sass), HTMX (Live feed polling)
* **Storage & Media:** WhiteNoise (Static files), AWS S3 / Boto3 (User-uploaded flag images)
* **Data Pipelines:** `feedparser` & `requests` (News feeds), `ijson` (Streaming large OCDS datasets)

---

## 📋 Prerequisites

Before setting up CivicEye locally, ensure you have the following installed on your machine:

1. **Python 3.10+** and `pip`
2. **Node.js** and `npm` (Required for Dart Sass compilation via `npx`)
3. **Git**
4. **PostgreSQL / Supabase Account** (Or local SQLite for quick offline testing)

---

## 🚀 Step-by-Step Local Setup Guide

Follow these steps in order to get the project up and running locally.

### Step 1: Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/civiceye.git](https://github.com/YOUR_USERNAME/civiceye.git)
cd civiceye
```

---

### Step 2: Create & Activate a Virtual Environment

* **On macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

* **On Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

* **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

---

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables (`.env`)

Create a `.env` file in the root directory of your project (same level as `manage.py`):

```bash
touch .env
```

Add the following environment configuration to your `.env` file:

```env
# Django Settings
SECRET_KEY=django-insecure-your-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=[http://127.0.0.1](http://127.0.0.1),http://localhost

# Database (Supabase Transaction Pooler - Port 6543)
DATABASE_URL=postgresql://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require
DB_SSL_REQUIRE=True

# Optional: AWS S3 Media Uploads (Leave empty to use local media folder)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=civiceye-media
AWS_S3_REGION_NAME=us-east-1
```

---

### Step 5: Pre-Compile Stylesheet (SCSS → CSS)

CivicEye uses Dart Sass to process styles. Compile the SCSS source file into standard CSS before running migrations or collecting static files:

```bash
npx sass static/scss/ud-styles.scss static/css/ud-styles.css
```

---

### Step 6: Run Database Migrations

Apply the database schema to your Supabase PostgreSQL instance (or local database):

```bash
python manage.py migrate
```

---

### Step 7: Download Dataset & Populate Initial Data

Because OCDS JSON datasets are large (often 100MB+), they are not stored in Git. Follow these sub-steps to download and stream the data:

1. **Download the OCDS Procurement Dataset:**
   * Visit the official Nigeria Open Contracting Portal: [http://nocopo.bpp.gov.ng/Open-Data](http://nocopo.bpp.gov.ng/Open-Data)
   * Download the latest **OCDS Contracting Release JSON** file.

2. **Place the File in the Project Directory:**
   Create a `data/` folder in your project root (if it doesn't exist) and place the downloaded file there, renaming it to `ContractingRelease.json`:
   ```bash
   mkdir -p data
   # Move your downloaded file into data/ContractingRelease.json
   ```

3. **Stream & Import OCDS Procurement Releases:**
   ```bash
   python manage.py import_ocds
   ```

4. **Fetch Categorized Government & Governance News:**
   ```bash
   python manage.py fetch_gov_news
   ```

---

### Step 8: Create an Admin Superuser

Create an administrative account to access the Django Admin Portal (`/admin`):

```bash
python manage.py createsuperuser
```

---

### Step 9: Collect Static Files

Collect all static assets (CSS, JS, images, fonts) into the static root directory:

```bash
python manage.py collectstatic --noinput
```

---

### Step 10: Start the Local Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## ⚙️ Automated Data Pipeline & Task Scheduling (GitHub Actions)

To automatically fetch and populate the latest news feeds into Supabase without manual commands or server costs, set up a GitHub Actions workflow.

Create a file named `.github/workflows/fetch_news.yml` in your repository:

```yaml
name: Automated News Ingestion Pipeline

on:
  schedule:
    # Runs automatically every 3 hours
    - cron: '0 */3 * * *'
  workflow_dispatch: # Allows manual trigger directly from GitHub UI

jobs:
  fetch-news:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Execute News Ingestion Script
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          python manage.py fetch_gov_news
```

> **Setting up Database Credentials on GitHub:**  
> Go to **GitHub Repo** → **Settings** → **Secrets and variables** → **Actions** → Click **New repository secret**.  
> Set the **Name** to `DATABASE_URL` and paste your Supabase connection URL string into the **Value**.

---

## 🌐 Production Deployment Notes (Render + Supabase)

When deploying to **Render**:

* **Build Command:**
  ```bash
  npx sass static/scss/ud-styles.scss static/css/ud-styles.css && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
  ```

* **Start Command:**
  ```bash
  gunicorn django_project.wsgi:application
  ```

* **Environment Variables on Render:**
  * Add `DATABASE_URL` pointing to your Supabase transaction pooler (`port: 6543`).
  * Add `PYTHON_VERSION` set to `3.11.0` (or your local python version).
