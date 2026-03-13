# ============================================================
# utils/preprocess.py — Text Cleaning Functions
# Cleans incoming messages before they are sent to the AI model.
# Removes URLs, special characters, extra whitespace, etc.
# ============================================================

import re

def clean_text(text: str) -> str:
    """
    Cleans raw message text for model input.
    - Removes URLs
    - Removes hashtags and @mentions
    - Removes special characters
    - Strips extra whitespace
    - Converts to lowercase
    """

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove @mentions
    text = re.sub(r"@\w+", "", text)

    # Remove hashtags
    text = re.sub(r"#\w+", "", text)

    # Remove special characters (keep letters, numbers, spaces, basic punctuation)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?']", "", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Lowercase
    text = text.lower()

    return text
