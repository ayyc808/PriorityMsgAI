#!/usr/bin/env python3
"""
Retrain Logistic Regression and Random Forest models on balanced dataset.
This fixes the over-classification issue by training on balanced Low/Medium examples.

Usage: python model_training/retrain_lr_rf.py
"""

import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from utils.preprocess import preprocess_text

# ── Configuration ──────────────────────────────────────────
DATA_PATH = "backend/data/balanced_training_data.csv"
OUTPUT_DIR = "backend/models"

LR_OUTPUT = os.path.join(OUTPUT_DIR, "lr_model.pkl")
RF_OUTPUT = os.path.join(OUTPUT_DIR, "rf_model.pkl")
TFIDF_OUTPUT = os.path.join(OUTPUT_DIR, "tfidf_vectorizer.pkl")

URGENCY_LABELS = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
LABEL_NAMES = ["Critical", "High", "Medium", "Low"]

print("=" * 70)
print("RETRAINING LOGISTIC REGRESSION & RANDOM FOREST MODELS")
print("=" * 70)

# ── Step 1: Load and Preprocess Data ──────────────────────
print("\n[1/6] Loading balanced training data...")
df = pd.read_csv(DATA_PATH)
print(f"   Loaded {len(df)} examples")
print(f"   Distribution: {df['urgency_level'].value_counts().to_dict()}")

print("\n[2/6] Preprocessing text...")
df["cleaned_text"] = df["text"].apply(preprocess_text)
df["label"] = df["urgency_level"].map(URGENCY_LABELS)

# Remove any rows with missing labels
df = df.dropna(subset=["label", "cleaned_text"])
print(f"   After cleaning: {len(df)} examples")

# ── Step 2: Split Data ─────────────────────────────────────
print("\n[3/6] Splitting train/test (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    df["cleaned_text"],
    df["label"],
    test_size=0.2,
    random_state=42,
    stratify=df["label"]  # Maintain class distribution
)
print(f"   Train size: {len(X_train)}")
print(f"   Test size: {len(X_test)}")

# ── Step 3: TF-IDF Vectorization ───────────────────────────
print("\n[4/6] Creating TF-IDF features...")
tfidf_vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),  # Unigrams and bigrams
    min_df=2,            # Ignore terms appearing in < 2 documents
    max_df=0.8,          # Ignore terms appearing in > 80% of documents
)

X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)
print(f"   Feature dimensions: {X_train_tfidf.shape}")

# ── Step 4: Train Logistic Regression ─────────────────────
print("\n[5/6] Training Logistic Regression...")
lr_model = LogisticRegression(
    max_iter=1000,
    random_state=42,
    class_weight='balanced',  # Handle class imbalance
    solver='lbfgs'
)
lr_model.fit(X_train_tfidf, y_train)

# Evaluate LR
lr_pred = lr_model.predict(X_test_tfidf)
lr_accuracy = accuracy_score(y_test, lr_pred)
print(f"   LR Test Accuracy: {lr_accuracy * 100:.2f}%")

# ── Step 5: Train Random Forest ────────────────────────────
print("\n[5/6] Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1  # Use all CPU cores
)
rf_model.fit(X_train_tfidf, y_train)

# Evaluate RF
rf_pred = rf_model.predict(X_test_tfidf)
rf_accuracy = accuracy_score(y_test, rf_pred)
print(f"   RF Test Accuracy: {rf_accuracy * 100:.2f}%")

# ── Step 6: Save Models ────────────────────────────────────
print("\n[6/6] Saving models...")
with open(LR_OUTPUT, "wb") as f:
    pickle.dump(lr_model, f)
print(f"   Saved: {LR_OUTPUT}")

with open(RF_OUTPUT, "wb") as f:
    pickle.dump(rf_model, f)
print(f"   Saved: {RF_OUTPUT}")

with open(TFIDF_OUTPUT, "wb") as f:
    pickle.dump(tfidf_vectorizer, f)
print(f"   Saved: {TFIDF_OUTPUT}")

# ── Detailed Evaluation ────────────────────────────────────
print("\n" + "=" * 70)
print("EVALUATION RESULTS")
print("=" * 70)

print("\nLOGISTIC REGRESSION")
print("-" * 70)
print(classification_report(y_test, lr_pred, target_names=LABEL_NAMES, zero_division=0))

print("\nRANDOM FOREST")
print("-" * 70)
print(classification_report(y_test, rf_pred, target_names=LABEL_NAMES, zero_division=0))

print("\n" + "=" * 70)
print("RETRAINING COMPLETE!")
print("=" * 70)
print("\nNext steps:")
print("1. Restart your FastAPI backend to load the new models")
print("2. Test classification with: cd backend && python3 classifier.py")
print("3. For RoBERTa retraining, use Google Colab (see instructions below)")
