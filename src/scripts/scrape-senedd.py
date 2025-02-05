#!/usr/bin/env python

from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path
import urllib.request
import json
import time
import re


DOMAIN = "https://record.senedd.wales"
ROOT_LIST_URL = f"{DOMAIN}/XMLExport/SeeMore"

TRANSCRIPTS = []

print( "=== BUILDING DOWNLOAD LIST ===" )
hasMore = True
page = 0
while( hasMore ):
  millisec = int(round(time.time() * 1000))
  generatedUrl = f"{ROOT_LIST_URL}?Committee=0&Page={page}&_{millisec}"

  print( f"  - Pulling {generatedUrl}" )
  with urllib.request.urlopen( generatedUrl ) as url:
      data = json.load( url )
      soup = BeautifulSoup( data['Html'] )

      for link in soup.findAll('a'):
        language = link.getText().lower()
        fqpath = f"{DOMAIN}{link.get('href')}"

        if language == 'bilingual':
          TRANSCRIPTS.append( fqpath )

      hasMore = data['MoreToShow']
      page = page + 1

print( "=== LOGGING SOURCES ===" )
with open( 'raw/sources.txt', 'w' ) as sources:
  for ts in TRANSCRIPTS:
    sources.write( f"{ts}\n" )
  sources.flush()

print( "=== DOWNLOADING TRANSCRIPTS ===" )

Path( "raw" ).mkdir( parents=True, exist_ok=True )
meetingPattern = re.compile( r"^.+meetingID=(\d+).*$" )
for url in tqdm( TRANSCRIPTS, desc="Downloading..." ):
  uid = re.match( meetingPattern, url ).group( 1 )
  urllib.request.urlretrieve( url, f"raw/{uid}.xml" )