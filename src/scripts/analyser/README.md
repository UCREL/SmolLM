# Model Training and Testing Tools

- `slurm_train.sh` - If running on the Hex cluster, or similar Slurm-based cluster, modify and use this file to control the training run on the batch system
- `test_model.py` - Tests the model in Welsh against the English counterpart
- `train_model.py` - Trains the model against a set of annotated files. See `xml2annotated.py` in the parent folder for how to generate these.

