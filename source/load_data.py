# 本程序: 导入拼音汉语对应关系, 并保存为本地json文件
import json

# 导入拼音汉字表
pinyin_word = {}
with open("../data/拼音汉字表.txt", "r", encoding="gbk") as f:
    for line in f:
        parse = line.split()
        pinyin_word[parse[0]] = []
        for i in range(1, len(parse)):
            pinyin_word[parse[0]].append(parse[i])
json_str = json.dumps(pinyin_word, ensure_ascii=False)
with open('../database/pinyin_word.json', 'w', encoding="gbk") as json_file:
    json_file.write(json_str)

# 导入整体汉字表
all_word = {}
all_word["all"] = []
with open("../data/一二级汉字表.txt", "r", encoding="gbk") as f:
    str = f.readlines()
    all_word["all"] = [i for i in str[0]]
json_str = json.dumps(all_word, ensure_ascii=False)
with open('../database/all_word.json', 'w', encoding="gbk") as json_file:
    json_file.write(json_str)
