import argparse
import torch
import os
import numpy as np
from evaluate import load as load_metric
from datasets import load_dataset, Value, ClassLabel, Sequence, Features
from transformers import AutoTokenizer, DataCollatorWithPadding, AutoModelForSequenceClassification, TrainingArguments, Trainer
import time
print( f"CUDA Available = {torch.cuda.is_available()}" )

BASE_MODEL = "distilbert-base-uncased"
SEED=int(time.time() * 1000)
TRAINING_DATASET = 3000

# Define the features
features = Features({
    'en': Value( dtype='string' ),
    'cy': Value( dtype='string' ),
    'score': Value( dtype='float32' ),
    'negative': Value( dtype='float32' ),
    'positive': Value( dtype='float32' ),
    'neutral': Value( dtype='float32' ),
    'label': ClassLabel( names=[ 'strongly positive', 'slightly positive', 'neutral', 'slightly negative', 'strongly negative' ] )
})

def compute_metrics(eval_pred):
   load_accuracy = load_metric("accuracy")
   load_f1 = load_metric("f1")

   logits, labels = eval_pred
   predictions = np.argmax(logits, axis=-1)
   accuracy = load_accuracy.compute(predictions=predictions, references=labels)["accuracy"]
   f1 = load_f1.compute(predictions=predictions, references=labels, average="macro")["f1"]

   return {"accuracy": accuracy, "f1": f1, "loss": 0}

def train_new_model( model, dataset = "../bilingual.json", samples = TRAINING_DATASET ):
   print( f"Training model {model} on dataset {dataset}", flush=True )
   dataset = load_dataset( "json", data_files=dataset, features=features )

   print( f"Loaded {dataset.num_rows} records!", flush=True )

   small_train_dataset = dataset['train'].shuffle(seed=SEED).select([i for i in list(range(samples))])
   small_test_dataset = dataset['train'].shuffle(seed=SEED).select([i for i in list(range(3000))])

   print( f"  - Training set: {small_train_dataset.num_rows} records", flush=True );
   print( f"  - Testing set: {small_test_dataset.num_rows} records", flush=True );

   tokenizer = AutoTokenizer.from_pretrained( BASE_MODEL )
   data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

   def preprocess_function(examples):
      return tokenizer(examples["cy"], truncation=True)
   
   tokenized_train = small_train_dataset.map(preprocess_function, batched=True)
   tokenized_test = small_test_dataset.map(preprocess_function, batched=True)

   newModel = None
   if os.path.exists( model ):
      print( f"Loading model from {model}", flush=True )
      newModel = AutoModelForSequenceClassification.from_pretrained( model, num_labels=5 )
   else:
      print( f"Creating new model {model}", flush=True )
      newModel = AutoModelForSequenceClassification.from_pretrained( BASE_MODEL, num_labels=5 )
   
   training_args = TrainingArguments(
      output_dir=model,
      learning_rate=2e-5,
      per_device_train_batch_size=32,
      per_device_eval_batch_size=32,
      num_train_epochs=3,
      weight_decay=0.01,
      save_strategy="epoch"
   )
   
   trainer = Trainer(
      model=newModel,
      args=training_args,
      train_dataset=tokenized_train,
      eval_dataset=tokenized_test,
      tokenizer=tokenizer,
      data_collator=data_collator,
      compute_metrics=compute_metrics,
   )

   trainer.train()
   trainer.save_model( model )

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument( "-m", "--model", help="Model to train", default="cy-sentiment-finetune" )
   parser.add_argument( "-d", "--dataset", help="Dataset to train on", default="../bilingual.json" )
   parser.add_argument( "-s", "--samples", help="The number of samples to train the model on", default=TRAINING_DATASET )
   
   args = parser.parse_args()

   # This is a stupid hack to get the model name sorted. Needs to be refactored really...
   model_name = f"{args.model}-{int(args.samples)}"

   train_new_model( model = model_name, dataset=args.dataset, samples=int(args.samples) )