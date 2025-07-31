#!/bin/bash
#SBATCH --partition=a5000-48h
#SBATCH --output=training.log

python3 train_model.py \
        -m "cy-sentiment-finetune" \
        -d "../bilingual.json" \
        -s 1000000
