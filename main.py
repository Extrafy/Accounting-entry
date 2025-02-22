from transformers import BertTokenizer,BertForSequenceClassification
import torch
import json
from transformers import BertForSequenceClassification, BertTokenizer
import torch
import re
import sparkAPI

appid="1deed739"
api_secret="MGU0MWY2ZTU1M2U0NjZhNjAyNGExYWY2"
api_key="658cf576a49146f83fbacafef411e38f"
gpt_url="wss://spark-api.xf-yun.com/v3.5/chat"
domain="generalv3.5"
print("数字提取器加载完毕！")

tokenizer_0 = BertTokenizer.from_pretrained("借方分词器")
model_0 = BertForSequenceClassification.from_pretrained("借方分类器.pth")
print("借方科目分词器加载完毕！")

tokenizer_1 = BertTokenizer.from_pretrained("贷方分词器")
model_1 = BertForSequenceClassification.from_pretrained("贷方分类器.pth")
print("贷方科目分词器加载完毕！")

# 读取 JSON 文件并将其转换为字典
with open('dict.json', 'r') as file:
    data = json.load(file)

def get_prediction(tokenizer, model, text, data):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    logits = outputs.logits
    sorted_indexes = torch.argsort(logits, dim=-1, descending=True).squeeze()
    return sorted_indexes

def print_entry(side, predicted_class_index, data, num):
    predicted_class = list(data.keys())[predicted_class_index]
    print(f"{side}：{predicted_class}                ",end='')
    sparkAPI.get_num(query)
    print(" 元")

def get_text(text,label1,label2):
    query="我现在有一笔交易事项，具体是\""+text+"\"在进行会计分录时，借方科目是“"\
        +label1+"”，而贷方科目是“"+label2+\
        "”。直接给出这种情况下借方和贷方的金额数目的数值。注意，你的回答只能包含一个数字，不能有任何其他的推理过程和汉字。"
    return query

"""
def get_num(text):
    pattern = r'(\d+\.?\d*)[元百千万亿元]+'
    match = re.search(pattern, text)
    if match:
        amount = float(match.group(1))
        unit = text[match.start():match.end()]
        if '百' in unit:
            amount *= 100
        elif '千' in unit:
            amount *= 1000
        elif '万' in unit:
            amount *= 10000
        elif '亿' in unit:
            amount *= 100000000
        return round(amount, 2)
    else:
        return None
 """


while True:
    print("---------------------------------")
    text = input("请输入您需要处理的语句：\n")

    print("\n生成的会计分录如下：")
   
    sorted_indexes_0 = get_prediction(tokenizer_0, model_0, text, data)
    sorted_indexes_1 = get_prediction(tokenizer_1, model_1, text, data)
    query = get_text(text,list(data.keys())[sorted_indexes_0[0].item()],list(data.keys())[sorted_indexes_1[0].item()])
    
    print_entry("借", sorted_indexes_0[0].item(), data, query)
    print_entry("  贷", sorted_indexes_1[0].item(), data, query)

    correction_index_0 = 0
    correction_index_1 = 0
    
    
    while True:
        flag = int(input("该会计分录是否正确？（正确请输入0，借方科目错误请输入1，贷方科目错误请输入2，金额错误请输出3）\n"))
        if flag == 0:
            break
        elif flag == 1:
            print("请稍后，正在重新生成......")
            correction_index_0 += 1
            query = get_text(text,list(data.keys())[sorted_indexes_0[correction_index_0].item()],list(data.keys())[sorted_indexes_1[correction_index_1].item()])
            print_entry("借", sorted_indexes_0[correction_index_0].item(), data, query)
            print_entry("  贷", sorted_indexes_1[correction_index_1].item(), data, query)
        elif flag == 2:
            correction_index_1 += 1
            query = get_text(text,list(data.keys())[sorted_indexes_0[correction_index_0].item()],list(data.keys())[sorted_indexes_1[correction_index_1].item()])
            print_entry("借", sorted_indexes_0[correction_index_0].item(), data, query)
            print_entry("  贷", sorted_indexes_1[correction_index_1].item(), data, query)
        else:
            query = get_text(text,list(data.keys())[sorted_indexes_0[correction_index_0].item()],list(data.keys())[sorted_indexes_1[correction_index_1].item()])
            print_entry("借", sorted_indexes_0[correction_index_0].item(), data, query)
            print_entry("  贷", sorted_indexes_1[correction_index_1].item(), data, query)
    
    print()
