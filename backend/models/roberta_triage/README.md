# models/roberta_triage/

This folder contains the fine-tuned RoBERTa model for emergency message urgency classification.

## Model Details
- Base model: roberta-base (125M parameters)
- Fine-tuned on: 80,339 crisis messages across 4 datasets
- Task: 4-class urgency classification (Critical / High / Medium / Low)
- Training: We did 3 epochs on Google Colab T4 GPU hardware accelerator
- Best F1 Score: 0.851 | Accuracy: 84.8%

## Files
- `model.safetensors` — trained model weights (498.6 MB)
- `config.json` — model architecture configuration
- `tokenizer.json` — RoBERTa tokenizer
- `tokenizer_config.json` — tokenizer settings
- `training_args.bin` — training hyperparameters

## Usage
```python
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

model = RobertaForSequenceClassification.from_pretrained("backend/models/roberta_triage")
tokenizer = RobertaTokenizer.from_pretrained("backend/models/roberta_triage")
```

## Note
These files are large and have been excluded from GitHub via .gitignore.
To regenerate, run the RoBERTa Colab notebook in model_training/notebooks/