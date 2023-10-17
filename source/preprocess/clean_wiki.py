# 本程序: 清理文本并保存为json文件
import json
import re
import os

def get_all_path(open_file_path):
    rootdir = open_file_path
    path_list = []
    
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    
    for i in range(0, len(list)):
        com_path = os.path.join(rootdir, list[i])
       
        if os.path.isfile(com_path):
            path_list.append(com_path)
        if os.path.isdir(com_path):
            path_list.extend(get_all_path(com_path))
            

    return path_list



file_list = get_all_path("../data/wiki_zh")
# print(file_list)



# 清洗并存入
def clean_input(dict, name, sen_list):
    dict[name] = re.sub("（(.*?)）","",dict[name])
    dict[name] = re.sub("\((.*?)\)","",dict[name])
    sen_list.extend(re.split('[，,。.？?！!▲【】；…~\s〜]', dict[name]))


# 数据清理
raw_sentence_list = []
for file in file_list:
    file_path = file
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            dict = json.loads(line)
            clean_input(dict, "text", raw_sentence_list)


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
with open('../database/sentence_wiki.json', 'w', encoding="utf-8") as json_file:
    json_file.write(json_str)
