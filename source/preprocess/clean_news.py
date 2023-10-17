# 本程序: 清理文本并保存为json文件
import json
import re

file_list = ["news2016zh_valid.json", "news2016zh_train.json"]
path = "../data/"

# 清洗并存入
def clean_input(dict, name, sen_list):
    dict[name] = re.sub("（(.*?)）","",dict[name])
    dict[name] = re.sub("\((.*?)\)","",dict[name])
    sen_list.extend(re.split('[，,。.？?！!▲【】；…~\s〜]', dict[name]))


# 数据清理
raw_sentence_list = []
for file in file_list:
    file_path = path + file
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            dict = json.loads(line)
            clean_input(dict, "title", raw_sentence_list)
            clean_input(dict, "desc", raw_sentence_list)
            clean_input(dict, "content", raw_sentence_list)


sentence_list = []
for sen in raw_sentence_list:
    if len(sen):
        sen = re.sub(r'''[“”#《》—‘’@、><…￥:：·"*'{}]''',"",sen)
        if len(sen):
            sentence_list.append(sen)
del raw_sentence_list

# 保存结果
all_sentence = {}
all_sentence["all"] = sentence_list[:30000000]
json_str = json.dumps(all_sentence, ensure_ascii=False)
with open('../database/sentence_news.json', 'w', encoding="utf-8") as json_file:
    json_file.write(json_str)
