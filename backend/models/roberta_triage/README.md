# models/roberta_triage/

This folder will contain the saved fine-tuned RoBERTa model files after training.

Files that will appear here after running train.py:
- config.json
- pytorch_model.bin
- tokenizer_config.json
- vocab.json
- merges.txt

To generate these files, run:
    python model_training/train.py

These files are large and are excluded from GitHub via .gitignore.
