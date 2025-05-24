#!/usr/bin/env python

import argparse
import json
import time

def llm_translate( source, target="English" ):
    return "No translation available"

if __name__ == "__main__":
    parser = argparse.ArgumentParser( description="Build a prompt file from a supplied txt file" )
    parser.add_argument( '--lang', '-l', type=str, default="cy", help="Language code to record" )
    parser.add_argument( '--min', type=int, default=30, help="Minimum sample text to use, skips samples shorter than this value" )
    (args, opts) = parser.parse_known_args()

    MIN_LENGTH = args.min

    print( "[\n" )

    for path in opts:
        readBytes = 0
        buffer = []
        frame = []
        with open( path, "r" ) as f:
            while f.readable():
                data = f.read(1)
                readBytes = readBytes + 1

                if buffer not in ['\n', '\r']:
                    buffer.append( data )

                if data == "":
                    break
                
                if data in ["\n", "!", "?", ".", '"'] and len(frame) == 0:
                    text = "".join(buffer).strip()

                    if len(text) < MIN_LENGTH:
                        buffer = []
                        continue

                    row = {
                        "en": llm_translate( text, "English" ),
                        args.lang: text,
                        "negative": 0.0,
                        "positive": 0.0,
                        "neutral": 0.0,
                        "score": 0.0,
                        "label": "neutral"
                    }
                    print( f"{json.dumps(row)}," )

                    buffer = []
                    continue
                    
                if data in [ "(", "[", "{", "<", '"' ]:
                    frame.append( data )
                    continue
                    
                if data in [ ")", "]", "}", ">" ]:
                    #print( len(frame), data, "".join(buffer) )
                    # Are we folding in a quote?
                    if len(frame) > 0:
                        if( frame[-1] == "(" and data == ")" ) or ( frame[-1] == "[" and data == "]" ) or \
                           ( frame[-1] == "{" and data == "}" ) or ( frame[-1] == "<" and data == ">" ) or ( frame[-1] == '"' and data == '"' ):
                            #print( len(frame), data, "".join(buffer) )
                            buffer.append( data )
                            frame.pop()
                            continue
                        frame.pop()
                        continue
                    frame.append( data )
                    continue

        print( "]\n" )