import json
from pypinyin import pinyin, Style

file_list = ["sentence_wiki.json", "sentence_baike.json", "sentence_news.json", "sentence_web.json"]

word_dict = {}
for file in file_list:
    f = open("../database/" + file, "r", encoding="utf-8")
    sentence_list = json.load(f)
    f.close()
    # 计算句首字的概率
    cnt = 0
    for sen in sentence_list["all"]:
        if cnt%10000 == 0:
            print("%d/%d"%(cnt, len(sentence_list["all"])))
        cnt += 1
        if not len(sen):
            continue
        if pinyin(sen[0], style=Style.NORMAL,errors=lambda x: '*')[0][0] == '*':
            continue
        if sen[0] not in word_dict:
            word_dict[sen[0]] = 1
        else:
            word_dict[sen[0]] += 1

json_str = json.dumps(word_dict, ensure_ascii=False)
with open('../database/numres/starting.json', 'w', encoding="utf-8") as json_file:
    json_file.write(json_str)
    