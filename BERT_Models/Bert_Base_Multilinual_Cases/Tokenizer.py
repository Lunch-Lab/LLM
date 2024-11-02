from transformers import TFBertTokenizer,BertTokenizer,TFBertModel

vacab_path="https://huggingface.co/bert-base-multilingual-cased/resolve/main/vocab.txt"
import requests
rq_vacab=requests.get(vacab_path)
vocab=rq_vacab.text if rq_vacab.status_code==200 else None
with open("vocab.text","w") as f:
    f.write(vocab)