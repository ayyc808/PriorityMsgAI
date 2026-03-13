# ============================================================
# model_training/train.py — RoBERTa Model Training Script
# Fine-tunes a pre-trained RoBERTa model on crisis message data.
# Saves the trained model to backend/models/roberta_triage/
# Run with: python model_training/train.py
# ============================================================

import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
import torch

# ── Configuration ──────────────────────────────────────────
DATA_PATH = "backend/data/training_data.csv"
MODEL_OUTPUT_PATH = "backend/models/roberta_triage"
BASE_MODEL = "roberta-base"
MAX_LENGTH = 128
EPOCHS = 3
BATCH_SIZE = 16

# ── Label Maps ─────────────────────────────────────────────
URGENCY_LABELS = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

# ── Load Data ──────────────────────────────────────────────
def load_data():
    # TODO: Load and merge CrisisNLP, CrisisLex, and Kaggle datasets
    # For now loads the sample training_data.csv
    df = pd.read_csv(DATA_PATH)
    df["label"] = df["urgency_level"].map(URGENCY_LABELS)
    return df

# ── Tokenize ───────────────────────────────────────────────
def tokenize_data(texts, tokenizer):
    return tokenizer(
        list(texts),
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )

# ── Train ──────────────────────────────────────────────────
def train():
    print("Loading data...")
    df = load_data()

    print("Loading tokenizer and model...")
    tokenizer = RobertaTokenizer.from_pretrained(BASE_MODEL)
    model = RobertaForSequenceClassification.from_pretrained(BASE_MODEL, num_labels=len(URGENCY_LABELS))

    # TODO: Build full PyTorch Dataset class and Trainer setup
    # TODO: Add evaluation metrics (F1, precision, recall)
    # TODO: Save tokenizer and model after training

    print(f"Saving model to {MODEL_OUTPUT_PATH}...")
    model.save_pretrained(MODEL_OUTPUT_PATH)
    tokenizer.save_pretrained(MODEL_OUTPUT_PATH)
    print("Training complete.")

if __name__ == "__main__":
    train()
