import argparse
import torch
import os
import numpy as np
from evaluate import load as load_metric
from datasets import load_dataset, Value, ClassLabel, Sequence, Features
from transformers import AutoTokenizer, DataCollatorWithPadding, AutoModelForSequenceClassification, TrainingArguments, Trainer
import time
import json
from tqdm import tqdm
print( f"CUDA Available = {torch.cuda.is_available()}" )

DEFAULT_MODEL = "cy-sentiment-finetune-5000"
SEED=int(time.time() * 1000)

# Define the features
# features = Features({
#     'en': Value( dtype='string' ),
#     'cy': Value( dtype='string' ),
#     'score': Value( dtype='float32' ),
#     'negative': Value( dtype='float32' ),
#     'positive': Value( dtype='float32' ),
#     'neutral': Value( dtype='float32' ),
#     'label': ClassLabel( names=[ 'strongly positive', 'slightly positive', 'neutral', 'slightly negative', 'strongly negative' ] )
# })

def evaluate_model( model, dataset = "../bilingual.json", text = None ):
   loadedModel = AutoModelForSequenceClassification.from_pretrained( model, num_labels=5 )
   tokenizer = AutoTokenizer.from_pretrained(model)

   inputs = tokenizer( text, return_tensors="pt", truncation=True )

   with torch.no_grad():
       outputs = loadedModel( **inputs )
       logits = outputs.logits
       predicted_class_id = logits.argmax(dim=-1).item()

   labelClasses = [ 'strongly positive', 'slightly positive', 'neutral', 'slightly negative', 'strongly negative' ]

   return predicted_class_id, labelClasses[predicted_class_id]


if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument( "-m", "--model", help="Model to train", default=DEFAULT_MODEL )
   parser.add_argument( "-d", "--dataset", help="Dataset to train on", default="../bilingual.json" )
   parser.add_argument( "-f", "--file", required=True, help="The JSLOG file to process", default=None )
   
   args = parser.parse_args()

   labels = [ 'strongly positive', 'slightly positive', 'neutral', 'slightly negative', 'strongly negative' ]
   labels.reverse() # Because the classifier is trained with backwards labels (bug!)
   step = 1.0/len(labels)

   if not args.file:
      print( "No file specified, so nothing to do. Exiting", flush=True )
      exit( 0 )
   
   print( f"Processing file {args.file}", flush=True )
   with open( 'results.tsv', 'w' ) as results_file:
      with open( args.file, "r" ) as f:
         for line in tqdm( f, desc="Evaluating text...", leave=False, ncols=180 ):
            line = line.strip()
            if not line:
               continue
            
            row = json.loads( line )
            if "cy" not in row:
               print( f"Skipping line without text: {line}", flush=True )
               continue

            predicted_class_id, predicted_label = evaluate_model( model = args.model, dataset=args.dataset, text=row['cy'] )

            user_class_id = int(row['value']*(len(labels)-1) )
            user_label = labels[user_class_id]

            #print( f"{row['en']}" )
            #print( f"{predicted_class_id} ({predicted_label}) vs. {user_class_id} ({user_label})" )

            results_file.write( f"\"{row['en']}\"\t\"{row['cy']}\"\t{row['value']}\t\"{row['vote_language']}\"\t{predicted_class_id}\t\"{predicted_label}\"\t{user_class_id}\t\"{user_label}\"\n" )
            results_file.flush()
