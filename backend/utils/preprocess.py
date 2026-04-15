# ===========================================================================================================
# Practicing Data Quality (preprocessing unstructured data -> structured data) 
# ===========================================================================================================

"""
RapidRelief — utils/preprocess.py
Text cleaning and normalization pipeline.
 
All messages — whether from training datasets or user input via
the + Add Message interface — pass through this file before being
sent to the classification models.
 
The goal is to strip noise (URLs, hashtags, mentions, special chars)
and normalize text so the models receive clean, consistent input.
"""
 
import re
import string
 
# ---------------------------------------------------------------------------
# data cleaner helper functions
# Each function handles a specific task.
# and called in sequence by the main preprocess_text() function.
# ---------------------------------------------------------------------------
 
def to_lowercase(text: str) -> str:
    """
    Convert all characters to lowercase.
    Models are case-insensitive so this prevents 'FIRE' and 'fire'
    being treated as different tokens.
 
    Example:
        'FIRE ON MAIN STREET' → 'fire on main street'
    """
    return text.lower()
 
def remove_urls(text: str) -> str:
    """
    Remove http/https URLs from text.
    Social media posts often contain links that add no classification value.
 
    Example:
        'Check this out https://t.co/abc123 emergency!' → 'Check this out  emergency!'
    """
    # Matches http:// or https:// followed by any non-whitespace characters
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub('', text)
 
def remove_mentions(text: str) -> str:
    """
    Remove @username mentions from text.
    Twitter/social media handles are noise for classification.
 
    Example:
        '@911 help there is a fire' → ' help there is a fire'
    """
    # Matches @ followed by one or more word characters
    return re.sub(r'@\w+', '', text)
 
def remove_hashtag_symbols(text: str) -> str:
    """
    Strip the # symbol but keep the word itself.
    The word after # often contains useful emergency context.
 
    Example:
        '#fire #emergency help' → 'fire emergency help'
    """
    # Replace # followed by word characters with just the word
    return re.sub(r'#(\w+)', r'\1', text)
 
def expand_contractions(text: str) -> str:
    """
    Expand common English contractions to their full forms.
    Helps the model recognize words it was trained on.
 
    Example:
        "I can't breathe, there's smoke" → "I cannot breathe, there is smoke"
    """
    # Dictionary of common contractions and their expansions
    contractions = {
        "can't": "cannot",
        "won't": "will not",
        "don't": "do not",
        "doesn't": "does not",
        "didn't": "did not",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "haven't": "have not",
        "hasn't": "has not",
        "hadn't": "had not",
        "wouldn't": "would not",
        "couldn't": "could not",
        "shouldn't": "should not",
        "i'm": "i am",
        "i've": "i have",
        "i'll": "i will",
        "i'd": "i would",
        "it's": "it is",
        "that's": "that is",
        "there's": "there is",
        "they're": "they are",
        "they've": "they have",
        "they'll": "they will",
        "we're": "we are",
        "we've": "we have",
        "we'll": "we will",
        "you're": "you are",
        "you've": "you have",
        "you'll": "you will",
        "he's": "he is",
        "she's": "she is",
        "what's": "what is",
        "who's": "who is",
        "let's": "let us",
    }
 
    # Sort by length descending so longer contractions match first
    for contraction, expansion in sorted(contractions.items(), key=lambda x: len(x[0]), reverse=True):
        # Use word boundaries to avoid partial matches
        text = re.sub(r'\b' + re.escape(contraction) + r'\b', expansion, text, flags=re.IGNORECASE)
 
    return text
 
def convert_emojis_to_text(text: str) -> str:
    """
    Convert common urgency-related emojis to text tokens.
    Emojis in emergency messages often signal urgency level.
    Only maps the most common emergency-relevant emojis.
 
    Example:
        '🔥 fire on main st' → 'fire fire on main st'
        '🚨 emergency' → 'emergency emergency'
    """
    emoji_map = {
        '🔥': 'fire',
        '🚨': 'emergency',
        '🆘': 'sos',
        '⚠️': 'warning',
        '🚒': 'fire truck',
        '🚑': 'ambulance',
        '🚓': 'police',
        '💊': 'medical',
        '🌊': 'flood',
        '🌪️': 'tornado',
        '💨': 'wind',
        '🏥': 'hospital',
        '❗': 'urgent',
        '❕': 'urgent',
        '🆘': 'help',
        '😱': 'panic',
        '😨': 'scared',
    }
 
    for emoji, token in emoji_map.items():
        text = text.replace(emoji, f' {token} ')
 
    return text
 
def remove_special_characters(text: str) -> str:
    """
    Remove punctuation and special characters.
    Keeps only letters, numbers, and spaces.
    Numbers are kept because they can indicate severity
    (e.g. '5 people trapped', 'floor 3').
 
    Example:
        'help!!! there???s a fire @#$%' → 'help theres a fire '
    """
    # Keep only alphanumeric characters and spaces
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)
 
def normalize_whitespace(text: str) -> str:
    """
    Collapse multiple spaces, tabs, and newlines into a single space.
    Strip leading and trailing whitespace.
 
    Example:
        '  help   there  is  a   fire  ' → 'help there is a fire'
    """
    # Replace any sequence of whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
 
# ---------------------------------------------------------------------------
# Main preprocessing function
# This will be the only function called by classifier.py and the classify route.
# should run helper functions in the proper order.
# ---------------------------------------------------------------------------
 
def preprocess_text(text: str) -> str:
    """
    Full cleaning and normalization pipeline for emergency messages.
 
    Applies transformations in this order:
    1. Convert emojis to text tokens (before lowercasing to preserve emoji detection)
    2. Lowercase
    3. Expand contractions
    4. Remove URLs
    5. Remove @mentions
    6. Remove hashtag # symbols (keep the word)
    7. Remove special characters
    8. Normalize whitespace
 
    Args:
        text (str): Raw message string from user input or dataset
 
    Returns:
        str: Cleaned and normalized text ready for model input
 
    Example:
        Input:  "Help!! A man is stuck in elevator #emergency @911 https://t.co/abc 🚨"
        Output: "help a man is stuck in elevator emergency emergency"
    """
    if not text or not isinstance(text, str):
        return ""                               # guard against None or non-string input
 
    text = convert_emojis_to_text(text)         # emojis → text tokens
    text = to_lowercase(text)                   # normalize case
    text = expand_contractions(text)            # removes apos -> can't → cannot
    text = remove_urls(text)                    # strip links
    text = remove_mentions(text)                # strip @handles
    text = remove_hashtag_symbols(text)         # strip hashtags #fire → fire
    text = remove_special_characters(text)      # strip punctuation
    text = normalize_whitespace(text)           # clean up spaces
 
    return text
 
# Ran as single test this file directly to verified the pipeline works

if __name__ == "__main__":
 
    # These test messages mirror the fake messages as mentioned in section 3.6 of the doc
    # plus edge cases with URLs, mentions, emojis, and special characters
    test_messages = [
        # From the doc's test message table
        "There is a strong smell of gas coming from the basement of the apartment complex on 5th Ave. People are starting to feel dizzy.",
        "I can see smoke and orange flames on the ridge behind the high school. The wind is picking up and blowing towards the houses.",
        "I have run out of my prescription heart medication and the roads are blocked by snow.",
        "I've had a scratchy throat and a mild cough for two days. No fever or trouble breathing. Are there any local clinics open today?",
 
        # Social media style with noise
        "Help! A man is stuck in an elevator of an old abandoned building #help #emergency",
        "Smoke coming from downtown!??@ #help #fire https://t.co/abc123",
        "@911 @police there's a shooter on campus HELP!!!",
 
        # Emoji heavy
        "🔥 fire on main street 🚨 call 911 now ❗",
        "🌊 flooding near highway 101 people trapped 🆘",
 
        # Edge cases
        "",           # empty string
        None,         # None input — should not crash
        "   ",        # whitespace only
        "FLOOD WARNING: River levels rising fast near Hwy 101!!!",
    ]
 
    print("=" * 60)
    print("RapidRelief — preprocess.py test run")
    print("=" * 60)
 
    for i, msg in enumerate(test_messages):
        result = preprocess_text(msg)
        print(f"\n[{i+1}] Input:  {repr(msg)}")
        print(f"     Output: {repr(result)}")
 
    print("\n" + "=" * 60)
    print("All tests complete.")
 