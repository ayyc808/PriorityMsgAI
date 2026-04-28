"""
RapidRelief — classifier.py
Loads all three trained models and runs inference on cleaned text.

This file is imported by routes/classify.py and called on every
message submitted via the + Add Message interface.

Models loaded:
    - RoBERTa (primary)         → backend/models/roberta_triage/
    - Logistic Regression       → backend/models/lr_model.pkl
    - Random Forest             → backend/models/rf_model.pkl
    - TF-IDF Vectorizer         → backend/models/tfidf_vectorizer.pkl
"""

import pickle
import torch
import numpy as np
import os
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from utils.preprocess import preprocess_text

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR      = os.path.join(BASE_DIR, "models")
ROBERTA_PATH    = os.path.join(MODELS_DIR, "roberta_triage")
LR_PATH         = os.path.join(MODELS_DIR, "lr_model.pkl")
RF_PATH         = os.path.join(MODELS_DIR, "rf_model.pkl")
TFIDF_PATH      = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")

# ---------------------------------------------------------------------------
# Label mappings
# ---------------------------------------------------------------------------

# RoBERTa will use integer labels internally
ID2LABEL = {0: "Critical", 1: "High", 2: "Medium", 3: "Low"}
LABEL2ID = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

# Urgency score mapping will be used for priority queue sorting
# Higher score means higher priority
URGENCY_SCORES = {
    "Critical": 1.0,
    "High":     0.75,
    "Medium":   0.50,
    "Low":      0.25,
}

# Emergency category keywords
# Used to determine emergency type from message content
CATEGORY_KEYWORDS = {
    "Fire":          ["fire", "flame", "smoke", "burning", "blaze", "wildfire", "arson"],
    "Flood":         ["flood", "flooding", "water", "river", "dam", "submerged", "inundation"],
    "Medical":       ["medical", "injury", "injured", "heart", "ambulance", "hospital", "bleeding", "unconscious", "medication"],
    "Collapse":      ["collapse", "collapsed", "building", "structure", "rubble", "trapped"],
    "Shooting":      ["shooting", "shooter", "gunshot", "armed", "weapon", "gun"],
    "Explosion":     ["explosion", "exploded", "blast", "bomb", "detonation"],
    "Earthquake":    ["earthquake", "tremor", "seismic", "magnitude", "aftershock"],
    "Hurricane":     ["hurricane", "typhoon", "cyclone", "storm", "wind", "tornado"],
    "Environmental": ["gas", "chemical", "toxic", "spill", "leak", "hazmat", "pollution"],
    "Disaster":      ["disaster", "emergency", "crisis", "catastrophe", "evacuation"],
}

# ---------------------------------------------------------------------------
# Added critical override keywords
# So if RoBERTa predicts High but any of these severe keywords are present,
# they get bumped to to Critical urgency (may be better to over-alert(false positives)
# than under-alert(false negatives) in these  emergency situations)
# For ex, think of smoke alarms, false alarm vs a real catastrophic fire
# Over-alert Critical → dispatcher sends a unit → unit arrives → "it's under control, stand down" → minor inconvenience
# Under-alert Critical → dispatcher deprioritizes → delayed response → potential loss of life
# ---------------------------------------------------------------------------

CRITICAL_OVERRIDE_KEYWORDS = [
    # People in danger
    "trapped", "trapping", "pinned", "buried", "stuck",
    "unconscious", "unresponsive", "not breathing", "no pulse",
    "dead", "dying", "fatality", "fatalities", "casualties",
    "missing person", "missing child",

    # Structural emergencies
    "collapsed", "collapse", "collapses", "collapsing",
    "explosion", "exploded", "blast", "detonation",
    "structural failure", "building failure",

    # Medical emergencies
    "heart attack", "cardiac arrest", "stroke", "seizure",
    "overdose", "overdosed", "not responsive",
    "severe bleeding", "blood loss", "hemorrhage",
    "anaphylaxis", "allergic reaction severe",

    # Mass casualty
    "mass casualty", "multiple casualties", "multiple injured",
    "multiple victims", "shooter", "shooting", "gunshot",
    "active shooter", "stabbing", "stabbed",

    # Immediate danger
    "help immediately", "need help now", "emergency now",
    "send help", "call 911", "life threatening",
    "life-threatening", "critical condition", "critical injury",
    "mayday", "sos", "rescue needed", "rescue immediately",

    # Fire emergencies
    "trapped in fire", "fire spreading", "wildfire spreading",
    "engulfed in flames", "flames spreading rapidly",

    # Flood/disaster
    "swept away", "being swept", "drowning", "submerged",
    "flash flood", "dam break", "levee breach",
]

def detect_category(text: str) -> str:
    """
    Detect emergency category from cleaned message text.
    Returns the category with the most keyword matches.
    Defaults to 'General' if no keywords match.
    """
    text_lower = text.lower()
    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score

    if not scores:
        return "General"

    return max(scores, key=scores.get)


# ---------------------------------------------------------------------------
# Model loading
# Models are loaded once when the server starts although not on every request
# This avoids the overhead of loading models repeatedly (about 500 MB)
# ---------------------------------------------------------------------------

print("Loading models...")

# Load RoBERTa
print("  Loading RoBERTa...")
roberta_tokenizer   = RobertaTokenizer.from_pretrained(ROBERTA_PATH)
roberta_model       = RobertaForSequenceClassification.from_pretrained(ROBERTA_PATH)
roberta_model.eval()

# Use GPU if available, otherwise CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
roberta_model = roberta_model.to(device)
print(f"  RoBERTa loaded on: {device}")

# Load Logistic Regression
print("  Loading Logistic Regression...")
with open(LR_PATH, "rb") as f:
    lr_model = pickle.load(f)

# Load Random Forest
print("  Loading Random Forest...")
with open(RF_PATH, "rb") as f:
    rf_model = pickle.load(f)

# Load TF-IDF Vectorizer
print("  Loading TF-IDF Vectorizer...")
with open(TFIDF_PATH, "rb") as f:
    tfidf_vectorizer = pickle.load(f)

print("All models loaded successfully!")


# ---------------------------------------------------------------------------
# Main classification function
# Called by routes/classify.py for every incoming message
# ---------------------------------------------------------------------------

def classify_message(raw_text: str) -> dict:
    """
    Classify a raw message using all three models.

    Steps:
    1. Clean text using preprocess.py pipeline
    2. Run RoBERTa inference (primary result)
    3. Run LR and RF inference (comparison)
    4. Detect emergency category
    5. Return unified result dictionary

    Args:
        raw_text (str): Raw message from user input

    Returns:
        dict: Classification results with urgency labels,
              confidence scores, and model breakdown
    """

    # Step 1: Preprocess clean the data
    cleaned_text = preprocess_text(raw_text)

    if not cleaned_text.strip():
        return {
            "error": "Message is empty after cleaning",
            "raw_text": raw_text,
        }

    # Step 2: RoBERTa inference live
    inputs = roberta_tokenizer(
        cleaned_text,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs     = roberta_model(**inputs)
        probs       = torch.softmax(outputs.logits, dim=-1)[0]
        roberta_id  = torch.argmax(probs).item()
        roberta_conf = probs[roberta_id].item()

    roberta_label = ID2LABEL[roberta_id]

    # Step 3: LR and RF inference
    tfidf_features = tfidf_vectorizer.transform([cleaned_text])

    lr_label    = lr_model.predict(tfidf_features)[0]
    lr_probs    = lr_model.predict_proba(tfidf_features)[0]
    lr_conf     = float(max(lr_probs))

    rf_label    = rf_model.predict(tfidf_features)[0]
    rf_probs    = rf_model.predict_proba(tfidf_features)[0]
    rf_conf     = float(max(rf_probs))

    # Step 4: Detect category
    category = detect_category(cleaned_text)


    # Step 5: Critical override check
    # Added so if RoBERTa predicts High but severe keywords are detected,
    # urgency gets escalate to Critical for better over-alert over under-alert
    # in life-threatening emergency situations
    final_label      = roberta_label
    override_applied = False
 
    if roberta_label == "High":
        # Added to check if any critical override keywords appear in the cleaned text
        text_lower = cleaned_text.lower()
        if any(kw in text_lower for kw in CRITICAL_OVERRIDE_KEYWORDS):
            final_label      = "Critical"
            override_applied = True

    # Step 6: Build and returns the result
    return {
        # Primary result from RoBERTa
        "raw_text":         raw_text,
        "cleaned_text":     cleaned_text,
        "urgency_label":    final_label,
        "urgency_score":    round(roberta_conf, 4),
        "category":         category,

        # each model breakdown
        # If the override was applied, the roberta model label will show the original
        # prediction with an override note for transparency
        "roberta_label":    f"{roberta_label} → Critical (override)" if override_applied else roberta_label,
        "roberta_score":    round(roberta_conf, 4),
        "lr_label":         lr_label,
        "lr_score":         round(lr_conf, 4),
        "rf_label":         rf_label,
        "rf_score":         round(rf_conf, 4),

        # Priority score uses final label after override
        "priority_score":   round(URGENCY_SCORES.get(final_label, 0.25), 4),
 
        # Transparency flag — lets frontend show override indicator to dispatcher
        # So dispatchers know when the system escalated a prediction
        "override_applied": override_applied,
    }


# ---------------------------------------------------------------------------
# Standalone test: Run it directly to verify that all models load and classify
# For Windows:    python classifier.py
# For Mac/Linux:  python3 classifier.py
# ---------------------------------------------------------------------------
 
if __name__ == "__main__":
    test_messages = [
        "Building collapsed people trapped inside need help immediately",
        "Smoke coming from downtown help fire",
        "Minor traffic accident no injuries reported",
        "Possible flooding near highway 101",
        "Person having heart attack at downtown plaza send ambulance now",
        "Active shooter reported on campus multiple casualties",
    ]
 
    print("\n" + "=" * 60)
    print("classifier.py standalone test")
    print("=" * 60)
 
    for msg in test_messages:
        result = classify_message(msg)
        print(f"\nMessage:  {msg}")
        print(f"Urgency:  {result['urgency_label']} ({result['urgency_score']})")
        print(f"Category: {result['category']}")
        print(f"RoBERTa:  {result['roberta_label']} ({result['roberta_score']})")
        print(f"LR:       {result['lr_label']} ({result['lr_score']})")
        print(f"RF:       {result['rf_label']} ({result['rf_score']})")
        print(f"Override: {result['override_applied']}")