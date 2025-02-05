import json
import torch
import numpy as np
from evaluate import load as load_metric
from datasets import load_dataset, Value, ClassLabel, Sequence, Features
from transformers import AutoTokenizer, DataCollatorWithPadding, AutoModelForSequenceClassification, TrainingArguments, Trainer
print( f"CUDA Available = {torch.cuda.is_available()}" )

BASE_MODEL = "distilbert-base-uncased"
SEED=42

# Define the features
features = Features({
    'en': Value( dtype='string' ),
    'cy': Value( dtype='string' ),
    'score': Value( dtype='float32' ),
    'negative': Value( dtype='float32' ),
    'positive': Value( dtype='float32' ),
    'neutral': Value( dtype='float32' ),
    'labels': ClassLabel( names=[ 'positive', 'neutral', 'negative' ] )
})

dataset = load_dataset( "json", data_files="../bilingual.json", features=features )

print( f"Loaded {dataset.num_rows} records!" )

small_train_dataset = dataset['train'].shuffle(seed=SEED).select([i for i in list(range(30000))])
small_test_dataset = dataset['train'].shuffle(seed=SEED).select([i for i in list(range(3000))])

print( f"  - Training set: {small_train_dataset.num_rows} records" );
print( f"  - Testing set: {small_test_dataset.num_rows} records" );

tokenizer = AutoTokenizer.from_pretrained( BASE_MODEL )
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

def preprocess_function(examples):
   return tokenizer(examples["cy"], truncation=True)
 
tokenized_train = small_train_dataset.map(preprocess_function, batched=True)
tokenized_test = small_test_dataset.map(preprocess_function, batched=True)

model = AutoModelForSequenceClassification.from_pretrained( BASE_MODEL, num_labels=2 )


 
def compute_metrics(eval_pred):
   load_accuracy = load_metric("accuracy")
   load_f1 = load_metric("f1")

   print(  "FIXFIXIFX" )
  
   logits, labels = eval_pred
   predictions = np.argmax(logits, axis=-1)
   accuracy = load_accuracy.compute(predictions=predictions, references=labels)["accuracy"]
   f1 = load_f1.compute(predictions=predictions, references=labels)["f1"]

   return {"accuracy": accuracy, "f1": f1, "loss": 0}
 
repo_name = "cy-sentiment-finetune-3000"
 
training_args = TrainingArguments(
   output_dir=repo_name,
   learning_rate=2e-5,
   per_device_train_batch_size=16,
   per_device_eval_batch_size=16,
   num_train_epochs=2,
   weight_decay=0.01,
   save_strategy="epoch"
)
 
trainer = Trainer(
   model=model,
   args=training_args,
   train_dataset=tokenized_train,
   eval_dataset=tokenized_test,
   tokenizer=tokenizer,
   data_collator=data_collator,
   compute_metrics=compute_metrics,
)

trainer.train()

#trainer.evaluate()