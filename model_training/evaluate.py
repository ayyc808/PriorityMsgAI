# ============================================================
# model_training/evaluate.py — Model Evaluation Script
# Tests the trained model and prints performance metrics.
# Metrics: Accuracy, F1-score, Precision, Recall
# Run with: python model_training/evaluate.py
# ============================================================

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

MODEL_PATH = "backend/models/roberta_triage"
DATA_PATH = "backend/data/training_data.csv"

URGENCY_LABELS = {0: "Critical", 1: "High", 2: "Medium", 3: "Low"}

def evaluate():
    print("Loading model and tokenizer...")
    tokenizer = RobertaTokenizer.from_pretrained(MODEL_PATH)
    model = RobertaForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()

    print("Loading test data...")
    df = pd.read_csv(DATA_PATH)

    # TODO: Split into proper test set (not training data)
    # TODO: Run predictions on test set
    # TODO: Print classification report

    print("Evaluation complete.")
    # Example output format:
    # print(classification_report(true_labels, predicted_labels, target_names=list(URGENCY_LABELS.values())))

if __name__ == "__main__":
    evaluate()
