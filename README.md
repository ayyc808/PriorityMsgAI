# RapidRelief — AI-Powered Emergency Message Prioritization

An AI-powered emergency message triage system that classifies and ranks incoming emergency messages by urgency level using three machine learning models. Designed for dispatchers, analysts, and first responders to quickly identify and act on critical situations.

**Models used:**
- RoBERTa (primary — fine-tuned transformer, 87.3% accuracy)
- Logistic Regression (comparison baseline, 80.5% accuracy)
- Random Forest (comparison baseline, 78.0% accuracy)

---

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Dataset Setup](#3-dataset-setup)
  - [4. Model Setup](#4-model-setup)
  - [5. Frontend Setup](#5-frontend-setup)
- [Running the App](#running-the-app)
- [API Documentation](#api-documentation)
- [Team](#team)

---

## Project Structure

```
PRIORITYMSGAI/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── classifier.py            # Model inference + Critical override
│   ├── database.py              # SQLAlchemy models (SQLite)
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment secrets (not in GitHub)
│   ├── data/
│   │   ├── training_data.csv    # Labeled fake test messages
│   │   └── combine_crisislex.py # Script to combine CrisisLex datasets
│   ├── models/
│   │   ├── roberta_triage/      # Fine-tuned RoBERTa weights (not in GitHub)
│   │   ├── lr_model.pkl         # Trained LR model (not in GitHub)
│   │   ├── rf_model.pkl         # Trained RF model (not in GitHub)
│   │   └── tfidf_vectorizer.pkl # TF-IDF vectorizer (not in GitHub)
│   ├── routes/
│   │   ├── auth.py              # Register + login endpoints
│   │   ├── classify.py          # Message classification endpoints
│   │   ├── notifications.py     # Notification endpoints
│   │   └── analytics.py         # Analytics endpoints
│   └── utils/
│       └── preprocess.py        # Text cleaning pipeline
├── frontend (tentative)/
├── model_training/
│   ├── notebooks/
│   │   ├── exploration.ipynb       # Dataset exploration + charts
│   │   ├── model_training.ipynb    # LR + RF training
│   │   ├── roberta_training.ipynb  # RoBERTa fine-tuning (run on Google Colab)
│   │   └── evaluation.ipynb        # Model comparison + evaluation
└── README.md
```

---

## Tech Stack

|           Layer          |                     Technology                    |
|--------------------------|---------------------------------------------------|
|         Frontend         |                   React, Vite                     |
|          Backend         |            Python, FastAPI, SQLAlchemy            |
|          Database        |                       SQLite                      |
|      Primary Model       |         RoBERTa (HuggingFace Transformers)        |
|     Comparison Models    | Logistic Regression, Random Forest (scikit-learn) |
|            Auth          |                 JWT (python-jose)                 |
|      Version Control     |                       GitHub                      |

---

## Prerequisites

Make sure you have the following installed before starting:

### Mac/Linux
- Python 3.10+ → check with `python3 --version`
- Node.js 18+ → check with `node --version`
- Git → check with `git --version`

### Windows
- Python 3.10+ → download from https://python.org (check "Add to PATH" during install)
- Node.js 18+ → download from https://nodejs.org
- Git → download from https://git-scm.com

---

## Getting Started

### 1. Clone the Repository

**Mac/Linux:**
```bash
git clone https://github.com/ayyc808/PriorityMsgAI.git
cd PriorityMsgAI
```

**Windows:**
```bash
git clone https://github.com/ayyc808/PriorityMsgAI.git
cd PriorityMsgAI
```

---

### 2. Backend Setup

#### Step 1 — Create a virtual environment

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

#### Step 2 — Install Python dependencies

**Mac/Linux:**
```bash
cd backend
pip install -r requirements.txt
```

**Windows:**
```bash
cd backend
pip install -r requirements.txt
```

WARNING: torch is a large package (~700MB). Installation may take 3-5 minutes.

#### Step 3 — Create the .env file

Create a file called `.env` inside the `backend/` folder with the following content:

```
SECRET_KEY=rapidrelief_super_secret_key_change_this_later
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

WARNING: Do not commit this file to GitHub. It is already blocked by `.gitignore`.

#### Step 4 — Initialize the database

**Mac/Linux:**
```bash
python3 database.py
```

**Windows:**
```bash
python database.py
```

You should see: `Database initialized — prioritymsgai.db created.`

---

### 3. Dataset Setup

The large dataset files are not stored in GitHub. Each teammate must download them locally.

#### Required datasets — download and place in `backend/data/`:

|       Dataset       |                                               Source                                              |       Rename to       |
|---------------------|---------------------------------------------------------------------------------------------------|-----------------------|
|    Disaster Tweets  |                    https://www.kaggle.com/datasets/vstepanenko/disaster-tweets                    | `kaggle_disaster.csv` |
|     CrisisLexT26    |                            https://crisislex.org/data-collections.html                            | (folder — see below)  |
| CrisisNLP Benchmark | https://crisisnlp.qcri.org/data/crisis_datasets_benchmarks/crisis_datasets_benchmarks_v1.0.tar.gz | (extract — see below) |

#### Combine CrisisLex into one file:

After downloading and extracting CrisisLexT26, run:

**Mac/Linux:**
```bash
python3 data/combine_crisislex.py /path/to/your/CrisisLexT26
```

**Windows:**
```bash
python data/combine_crisislex.py C:\path\to\your\CrisisLexT26
```

This creates `backend/data/crisislex_combined.csv`.

#### Extract CrisisNLP files:

**Mac/Linux:**
```bash
tar -xvf ~/Downloads/crisis_datasets_benchmarks.tar.gz -C ~/Downloads/
cp ~/Downloads/data/all_data_en/crisis_consolidated_humanitarian_filtered_lang_en_train.tsv backend/data/crisisnlp_train.tsv
cp ~/Downloads/data/all_data_en/crisis_consolidated_humanitarian_filtered_lang_en_test.tsv backend/data/crisisnlp_test.tsv
cp ~/Downloads/data/all_data_en/crisis_consolidated_humanitarian_filtered_lang_en_dev.tsv backend/data/crisisnlp_dev.tsv
```

**Windows (PowerShell):**
```bash
tar -xvf crisis_datasets_benchmarks.tar.gz
copy data\all_data_en\crisis_consolidated_humanitarian_filtered_lang_en_train.tsv backend\data\crisisnlp_train.tsv
copy data\all_data_en\crisis_consolidated_humanitarian_filtered_lang_en_test.tsv backend\data\crisisnlp_test.tsv
copy data\all_data_en\crisis_consolidated_humanitarian_filtered_lang_en_dev.tsv backend\data\crisisnlp_dev.tsv
```

---

### 4. Model Setup

The trained model files are not stored in GitHub (as it is too large). You have two options you can do, Option A or Option B (for practice and understanding on training models (Google Colab recommended for T4 GPU as training large amt of data takes time - its free!)):

#### Option A — Get model files from  a teammate who has it
Ask a teammate who has already trained the models to share:
- `backend/models/lr_model.pkl`
- `backend/models/rf_model.pkl`
- `backend/models/tfidf_vectorizer.pkl`
- `backend/models/roberta_triage/` (entire folder)

Place them in the correct locations inside `backend/models/`.

#### Option B — Train the models yourself

**Train LR and RF locally:**

Open `model_training/notebooks/model_training.ipynb` in VSCode and run all cells. This saves `lr_model.pkl`, `rf_model.pkl`, and `tfidf_vectorizer.pkl` to `backend/models/`.

**Train RoBERTa on Google Colab (requires GPU):**

1. Go to https://colab.research.google.com
2. Upload `model_training/notebooks/roberta_training.ipynb`
3. Set Runtime → Change runtime type → T4 GPU
4. Run all cells
5. Download the generated `roberta_triage_final.zip`
6. Extract and place contents into `backend/models/roberta_triage/`

---

### 5. Frontend Setup

**Mac/Linux:**
```bash
cd ../frontend
npm install
```

**Windows:**
```bash
cd ..\frontend
npm install
```

---

## Running the App

### Start the Backend

**Mac/Linux:**
```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --reload
```

**Windows:**
```bash
cd backend
..\venv\Scripts\activate
uvicorn main:app --reload
```

WARNIING: First startup takes 30-60 seconds to load all three ML models.

Backend runs at: http://localhost:8000
API docs (Swagger UI): http://localhost:8000/docs

### Start the Frontend

Open a new terminal window:

**Mac/Linux:**
```bash
cd frontend
npm run dev
```

**Windows:**
```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:5173

---

## API Documentation

Once the backend is running, you can visit http://localhost:8000/docs for the full interactive Swagger UI with all available endpoints:

|    Section    | Endpoints |
|---------------|-----------|
|      Auth     | `POST /auth/register`, `POST /auth/login` |
|    Classify   | `POST /classify`, `GET /messages`, `POST /messages/{id}/save`, `POST /messages/{id}/archive`, `GET /messages/saved` |
| Notifications | `GET /notifications`, `GET /notifications/unread-count`, `PATCH /notifications/{id}/read`, `PATCH /notifications/read-all` |
|   Analytics   | `GET /analytics/overview`, `GET /analytics/urgency-distribution`, `GET /analytics/message-trends`, `GET /analytics/model-performance`, `GET /analytics/confidence-distribution`, `GET /analytics/category-breakdown`, `GET /analytics/recent-activity` |

---

## Testing the API with Swagger UI

Once the backend is running, go to http://localhost:8000/docs to test all endpoints interactively.

---

### Step 1 — Register an Account

1. Click `POST /auth/register` → **Try it out**
2. Paste the following into the request body:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@test.com",
  "password": "Test1234",
  "confirm_password": "Test1234",
  "organization": "Fire",
  "role": "Dispatcher"
}
```
3. Click **Execute**
4. Expected response `201`:
```json
{
  "message": "Account created successfully. Please log in.",
  "user_id": 1
}
```

---

### Step 2 — Login and Get JWT Token

1. Click `POST /auth/login` → **Try it out**
2. Paste:
```json
{
  "email": "john@test.com",
  "password": "Test1234"
}
```
3. Click **Execute**
4. Copy the `access_token` value from the response (without the quotes)

---

### Step 3 — Authorize Swagger UI

1. Click the **Authorize** button at the top right of the Swagger UI page
2. Paste the copied token into the value field
3. Click **Authorize** then **Close**

All subsequent requests will now include your JWT token automatically.

---

### Step 4 — Classify an Emergency Message

1. Click `POST /classify` → **Try it out**
2. Paste:
```json
{
  "text": "Building collapsed downtown people trapped inside need help immediately"
}
```
3. Click **Execute**
4. Expected response includes:
   - `urgency_label` — Critical, High, Medium, or Low
   - `category` — Collapse, Fire, Flood, Medical, etc.
   - `roberta_label`, `lr_label`, `rf_label` — all three model predictions
   - `override_applied` — true if Critical override keyword was triggered
   - `message_id` — ID saved to the database

---

### Step 5 — View Message Feed

1. Click `GET /messages` → **Try it out**
2. Leave parameters as default or filter by urgency (Critical/High/Medium/Low)
3. Click **Execute**
4. Returns all classified messages sorted by urgency score (highest first)

---

### Step 6 — Save a Message

1. Click `POST /messages/{message_id}/save` → **Try it out**
2. Enter the `message_id` from Step 4 (e.g. `1`)
3. Click **Execute**
4. Expected response:
```json
{
  "message": "Message saved successfully",
  "message_id": 1
}
```

---

### Step 7 — Check Notifications

1. Click `GET /notifications` → **Try it out**
2. Click **Execute**
3. Returns all notifications — Critical and High urgency messages auto-create notifications
4. Check `is_read: false` for unread notifications

---

### Step 8 — Mark Notification as Read

1. Click `PATCH /notifications/{notification_id}/read` → **Try it out**
2. Enter `1` in the `notification_id` field
3. Click **Execute**
4. Expected response:
```json
{
  "message": "Notification marked as read",
  "id": 1
}
```

---

### Step 9 — View Analytics

Test each analytics endpoint by clicking **Try it out** → **Execute**:

| Endpoint | What it returns |
|---|---|
| `GET /analytics/overview` | Total messages, urgency counts, avg confidence |
| `GET /analytics/urgency-distribution` | Counts and percentages per urgency level |
| `GET /analytics/message-trends` | Daily message volume for last 7 days |
| `GET /analytics/model-performance` | Agreement rates and confidence per model |
| `GET /analytics/confidence-distribution` | RoBERTa confidence score histogram |
| `GET /analytics/category-breakdown` | Emergency type distribution |
| `GET /analytics/recent-activity` | Last 10 classified messages |

---

### Step 10 — Archive a Message

1. Click `POST /messages/{message_id}/archive` → **Try it out**
2. Enter the `message_id`
3. Click **Execute**
4. Message is hidden from active feed but kept in database for analytics

---

## Common Issues You might run across

**`python` command not found (Mac):**
Use `python3` instead of `python` on Mac/Linux.

**`torch` install fails:**
Make sure you are using Python 3.10-3.13. Run `python3 --version` to check.

**`uvicorn` can't find `main` module:**
Make sure you are inside the `backend/` folder when running uvicorn.

**Models not found error on startup:**
Make sure all model files are in `backend/models/` — see Model Setup section above.

**Database not found:**
Run `python3 database.py` (Mac) or `python database.py` (Windows) from inside `backend/`.

---

## Team

|    Name   |        Role        | 
|-----------|--------------------|
|  Alvin C  | Software Developer |
| Malcolm D | Software Developer |
|   Minh T  |   SW QA Test Engr  |
| Richard P |  System Architect  |
|  Chan L   | Software Developer |

---