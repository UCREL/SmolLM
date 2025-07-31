# Scripts to Generate a Bilingual Welsh/English Sentiment Analyser

- `scrape-senedd.py` - Scrapes the Senedd on-line archive for bilingual text snippets
- `make-prompt.py` - Creates a 'prompt file' for use with SENTimental
- `xml2annotated.py` - Annotates the English text in the bilingual XML files from the Senedd, in preparation for training a new model
- `setup.sh` - Run on Linux-based hosts to install the required tools to run the other scripts.

For scripts for training and testing a model, see [the analyser/ path](analyser/)
