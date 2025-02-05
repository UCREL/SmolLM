#!/bin/bash



# Note that the below will have to be modified for non-Linux systems...
# See https://spacy.io/usage for other platforms
pip install -U pip setuptools wheel
pip install -U 'spacy[cuda12x]'
python -m spacy download en_core_web_trf
pip install -r requirements.txt