#!/usr/bin/env python

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from glob import glob
from tqdm import tqdm
import json
import spacy
import asent
import re
import sys

def parseXML( xmlfile ):
  texts = []

  try:
    tree = ET.parse( xmlfile )
    root = tree.getroot()

    for entry in root:
      lang = entry.find( 'contribution_language' ).text.lower()
      
      utterance = {}
      if lang == 'cy':
        utterance['cy'] = entry.find( 'contribution_verbatim' ).text
        utterance['en'] = entry.find( 'contribution_translated' ).text
      else:
        utterance['cy'] = entry.find( 'contribution_translated' ).text
        utterance['en'] = entry.find( 'contribution_verbatim' ).text
      
      if utterance['cy']:
        soup = BeautifulSoup( utterance['cy'], 'html.parser' )
        utterance['cy'] = soup.get_text( separator=' ', strip=True )

      if utterance['en']:
        soup = BeautifulSoup( utterance['en'], 'html.parser' )
        utterance['en'] = soup.get_text( separator=' ', strip=True )
      
      texts.append( utterance )

  except Exception as err:
    print( f"[WW]\tUnable to parse {xmlfile} - note that some Senedd files are empty, so fail to parse as valid XML...", flush=True )
    print( err, flush=True )

  return texts

# Note that these should match the UX scaled ones for SENTimental...
def weighted_polarity_label( score ):
  score = score * 100
  if score <= -25:
    return "strongly negative"
  
  if score <= -10:
    return "slightly negative"
  
  if score > 10:
    return "slightly positive"
  
  if score > 25:
    return "strongly positive"
  
  return "neutral"

if __name__ == "__main__":

  spacy.prefer_gpu()
  en_nlp = spacy.load( 'en_core_web_trf' )
  en_nlp.add_pipe( "asent_en_v1" )
  
  skipped_sentences = 0
  with open( "bilingual.json", "w", encoding="utf8" ) as bilingual:

    bilingual.write( "[\n" )

    for source in tqdm( glob( "raw/*.xml" ), desc="Extracting text...", leave=False, ncols=180 ):
      sys.stdout.flush()
      sys.stderr.flush()

      text = parseXML( source )

      for block in tqdm( text, desc="Block:            ", leave=False, ncols=180 ):
        sys.stdout.flush()
        sys.stderr.flush()

        if block['cy'] and block['en']:

          en_sentences = re.split( r'(\?|!|\.)', block['en'] )
          en_sentences = [i + j for i, j in zip(en_sentences[::2], en_sentences[1::2])]

          cy_sentences = re.split( r'(\?|!|\.)', block['cy'] )
          cy_sentences = [i + j for i, j in zip(cy_sentences[::2], cy_sentences[1::2])]

          if len(en_sentences) != len(cy_sentences):
            skipped_sentences = skipped_sentences + 1
            continue

          for idx, utterance in enumerate(tqdm(en_sentences, desc="Utterance:        ", leave=False, ncols=180 )):
            sys.stdout.flush()
            sys.stderr.flush()

            if len(utterance) < 10:
              continue

            doc = en_nlp( utterance )

            record = {
              "en": en_sentences[idx].strip(),
              "cy": cy_sentences[idx].strip(),
              "negative": doc._.polarity.negative,
              "positive": doc._.polarity.positive,
              "neutral": doc._.polarity.neutral,
              "score": doc._.polarity.compound,
              "label": weighted_polarity_label( doc._.polarity.compound )
            }

            bilingual.write( f"\t{json.dumps( record )},\n" )
    
    bilingual.write( "]" )

  #print( welsh )

  print( f"Skipped {skipped_sentences} sentences :(", flush=True  )