# PriorityMsgAI — Emergency Message Prioritizer

An AI-powered emergency message prioritization app that classifies and ranks incoming emergency notifications by urgency level and type. Designed for first responders and emergency coordinators to quickly identify critical situations and respond in a timely manner. 


## Project Structure

```
PriorityMsgAI/
├── backend/          # FastAPI backend + AI model
├── frontend/         # React frontend dashboard
├── model_training/   # RoBERTa training and evaluation scripts
└── README.md
```

---

## How to Run Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs at: http://localhost:8000

### Frontend
```bash
cd frontend
npm install
npm start
```
Frontend runs at: http://localhost:3000

## Team

| Name | Role |



## Tech Stack

- **Frontend:** React
- **Backend:** Python, FastAPI
- **AI Model:** RoBERTa (HuggingFace Transformers)
- **Version Control:** GitHub
