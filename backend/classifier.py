# ============================================================
# classifier.py — AI Model Loader & Prediction Engine
# Loads the fine-tuned RoBERTa model and runs predictions.
# Returns urgency level, emergency type, and confidence score.
# ============================================================

from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

# Labels the model will predict
URGENCY_LEVELS = ["Critical", "High", "Medium", "Low"]
EMERGENCY_TYPES = ["Disaster", "Medical", "Environmental"]

# TODO: Load tokenizer and model from the saved model folder
# tokenizer = RobertaTokenizer.from_pretrained("models/roberta_triage")
# model = RobertaForSequenceClassification.from_pretrained("models/roberta_triage")

def classify_message(text: str) -> dict:
    """
    Takes a raw message string and returns:
    - urgency_level: Critical, High, Medium, or Low
    - emergency_type: Disaster, Medical, or Environmental
    - urgency_score: confidence score between 0.0 and 1.0
    """

    # TODO: Replace with real model inference once model is trained
    # Step 1: Clean and tokenize the text
    # Step 2: Run through model
    # Step 3: Extract predicted urgency level and emergency type
    # Step 4: Return results

    # Placeholder response for development
    return {
        "urgency_level": "Critical",
        "emergency_type": "Disaster",
        "urgency_score": 0.95
    }
