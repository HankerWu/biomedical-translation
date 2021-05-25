from datasets import load_metric
from transformers import (MBartForConditionalGeneration, MBartTokenizer,
                          Seq2SeqTrainingArguments, Seq2SeqTrainer)
import config


def get_data_dict(data_path):
    data = []
    with open(data_path + '.en') as f1, open(data_path + '.zh') as f2:
        for src, tgt in zip(f1, f2):
            data.append(
                {"translation": {
                    "en": src.strip(),
                    "zh": tgt.strip()
                }})

    return data

model = MBartForConditionalGeneration.from_pretrained(
    "facebook/mbart-large-cc25")
tokenizer = MBartTokenizer.from_pretrained("facebook/mbart-large-cc25")

metric = load_metric("metric.py")
max_input_length = 256
max_target_length = 256


def data_collator(features: list):

    labels = [f['translation']['zh'] for f in features]
    inputs = [f['translation']['en'] for f in features]

    batch = tokenizer.prepare_seq2seq_batch(src_texts=inputs,
                                            src_lang="en_XX",
                                            tgt_lang="zh_CN",
                                            tgt_texts=labels,
                                            max_length=64,
                                            max_target_length=64)

    for k in batch:
        batch[k] = torch.tensor(batch[k])

    return batch


data = []
data += get_data_dict(config.train_data_path)
data += get_data_dict(config.dev_data_path)
data += get_data_dict(config.test_data_path)

import torch
from torch.utils.data import random_split

split = 0.2
train_dataset, eval_dataset = random_split(
    data, lengths=[int((1 - split) * len(data)) + 1,
                   int(split * len(data))])


batch_size = 16
args = Seq2SeqTrainingArguments(
    "test-translation",
    evaluation_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=3,
    save_steps=5000,
    predict_with_generate=True,
    prediction_loss_only=True,
    fp16=True,
)

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
                         train_dataset=train_dataset,
                         eval_dataset=eval_dataset,
                         data_collator=data_collator,
                         tokenizer=tokenizer,
                         compute_metrics=compute_metrics)

trainer.train()
trainer.evaluate()

model.save_pretrained(config.model_dir)