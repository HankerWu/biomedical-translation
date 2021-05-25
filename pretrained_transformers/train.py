# model_checkpoint = "Helsinki-NLP/opus-mt-en-zh"

import config

from datasets import Dataset, load_metric

def get_data_dict(data_path):
    out_en_sent = []
    out_cn_sent = []

    with open(data_path + '.en', 'r+', encoding='utf-8') as en:
        for line in en:
            out_en_sent.append(line[:-1])

    with open(data_path + '.zh', 'r+', encoding='utf-8') as zh:
        for line in zh:
            out_cn_sent.append(line[:-1])

    data_dict = {'en': out_en_sent,
                 'zh': out_cn_sent}
    return Dataset.from_dict(data_dict)

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(config.model_dir)
metric = load_metric("metric.py", num_process=4)
max_input_length = 256
max_target_length = 256

def preprocess_function(examples):
    inputs = examples['en']
    targets = examples['zh']
    model_inputs = tokenizer(inputs,
                             max_length=max_input_length,
                             truncation=True)

    # Setup the tokenizer for targets
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets,
                           max_length=max_target_length,
                           truncation=True)

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_train_data = get_data_dict(config.train_data_path).map(preprocess_function, batched=True)
tokenized_dev_data = get_data_dict(config.dev_data_path).map(preprocess_function, batched=True)
tokenized_test_data = get_data_dict(config.test_data_path).map(preprocess_function, batched=True)

from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
model = AutoModelForSeq2SeqLM.from_pretrained(config.model_dir)
model.init_weights()
# model.save_pretrained(config.model_dir)  # save
# model = model_class.from_pretrained(config.model_dir)  # re-load
# tokenizer.save_pretrained(config.model_dir)  # save
# tokenizer = BertTokenizer.from_pretrained(config.model_dir) # re-load


batch_size = 64
args = Seq2SeqTrainingArguments(
    "test-translation",
    evaluation_strategy="epoch",
    learning_rate=3e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=40,
    predict_with_generate=True,
    fp16=False,
)

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

import numpy as np


def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]

    return preds, labels


def compute_metrics(eval_preds):
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Some simple post-processing
    decoded_preds, decoded_labels = postprocess_text(decoded_preds,
                                                     decoded_labels)

    result = metric.compute(predictions=decoded_preds,
                            references=decoded_labels)
    result = {"bleu": result["score"]}

    prediction_lens = [
        np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds
    ]
    result["gen_len"] = np.mean(prediction_lens)
    result = {k: round(v, 4) for k, v in result.items()}
    return result


trainer = Seq2SeqTrainer(model,
                         args,
                         train_dataset=tokenized_train_data,
                         eval_dataset=tokenized_dev_data,
                         data_collator=data_collator,
                         tokenizer=tokenizer,
                         compute_metrics=compute_metrics)
                         
import torch
print(torch.cuda.current_device(), torch.cuda.device_count())
print('Start training...')

trainer.train()

model.save_pretrained(config.model_dir)  # save
# model = model_class.from_pretrained(config.model_dir)  # re-load
# tokenizer.save_pretrained(config.model_dir)  # save
# tokenizer = BertTokenizer.from_pretrained(config.model_dir) # re-load
