# 本程序: 清理文本并保存为json文件
import json
import re

file_list = ["2016-02.txt"] + [("2016-%02d.txt") % i for i in range(4, 12)]
path = "../data/sina_news/"

# 数据清理
raw_sentence_list = []
for file in file_list:
    file_path = path + file
    with open(file_path, "r", encoding="gbk") as f:
        for line in f:
            dict = json.loads(line)
            dict["title"] = re.sub("（(.*?)）","",dict["title"])
            dict["title"] = re.sub("\((.*?)\)","",dict["title"])
            dict["html"] = re.sub("（(.*?)）","",dict["html"])
            dict["html"] = re.sub("\((.*?)\)","",dict["html"])
            raw_sentence_list.extend(re.split('[：。？！▲【】；…\s]', dict["title"]))
            raw_sentence_list.extend(re.split('[：。？！▲【】；…\s]', dict["html"]))

sentence_list = []
for sen in raw_sentence_list:
    if len(sen):
        sen = re.sub('“',"",sen)
        sen = re.sub('”',"",sen)
        sen = re.sub('#',"",sen)
        sen = re.sub('《',"",sen)
        sen = re.sub('》',"",sen)
        sen = re.sub('，',"",sen)
        sen = re.sub('——',"",sen)
        sen = re.sub('‘',"",sen)
        sen = re.sub('’',"",sen)
        sen = re.sub('@',"",sen)
        sentence_list.append(sen)
del raw_sentence_list

# 保存结果
all_sentence = {}
all_sentence["all"] = sentence_list
json_str = json.dumps(all_sentence, ensure_ascii=False)
with open('../database/all_sentence.json', 'w', encoding="gbk") as json_file:
    json_file.write(json_str)
