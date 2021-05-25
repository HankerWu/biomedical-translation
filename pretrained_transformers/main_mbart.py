import argparse
from packaging.version import parse
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import load_metric
from nltk.tokenize import sent_tokenize
from get_pdf_content import PDF_Content
from nltk.tokenize import sent_tokenize
# 创建解析步骤
parser = argparse.ArgumentParser()

# 添加参数步骤
parser.add_argument('--pdf',
                    action="store_true",
                    help='whether input is pdf or not')
parser.add_argument('--field',
                    choices=['abstract', 'title', 'introduction','all'],
                    help='translation field')
parser.add_argument('--filename', help='name of file')

# 解析参数步骤
args = parser.parse_args()
print("argparse.args=", args, type(args))

tokenizer = AutoTokenizer.from_pretrained(
    "D:/MSRA/project/transformers_model/mbart/epoch2/")
# tokenizer.save_pretrained("D:/MSRA/project/transformers_model/mbart")
metric = load_metric("D:/MSRA/project/transformers/metric.py", num_process=4)

model = AutoModelForSeq2SeqLM.from_pretrained(
    "D:/MSRA/project/transformers_model/mbart/epoch3/")
text = []

if args.pdf:
    print('pdf mode.')
    pdf_content = PDF_Content(args.filename)
    pdf_content.getContent()
    if args.field == 'title':
        text = pdf_content.title
    elif args.field == 'abstract':
        text = pdf_content.abstract.split('\n')[1:]
    elif args.field == 'introduction':
        text = pdf_content.introduction.split('\n')[1:]
    else:
        text += [pdf_content.title+'\n']
        text += pdf_content.abstract.split('\n')
        text += pdf_content.introduction.split('\n')
else:
    print('txt mode.')
    # with open(args.filename, 'r') as f:
    #     text = f.read()

en_sent = []
for t in text:
    en_sent += sent_tokenize(t)
print('\n'.join(en_sent))

# model.to('cuda')
text = [
    "However, the within-host evolutionary dynamics of influenza viruses remain incompletely  understood, in part because most studies have focused on within-host virus diversity of  infections in otherwise healthy adults based on single timepoint data. ",
    "Early interactions with signiﬁcant individuals affect social experience throughout the course of a lifetime, as a repeated and prolonged perception of different levels of care, independence or control inﬂuences the modulation of emotional regulatory processes.",
    "Machine learning models showed that polygenetic risk score dominated \
                                over oral microbiome in predicting predisposing risk of dental diseases \
                                such as dental calculus and gingival bleeding."
]
# tokenized_text = tokenizer([text], return_tensors='pt').to('cuda')
tokenized_text = tokenizer(en_sent,
                           return_tensors='pt',
                           padding=True,
                           truncation=True)
translation = model.generate(**tokenized_text)
translated_text = tokenizer.batch_decode(translation, skip_special_tokens=True)
print('\n'.join(translated_text))