import json

file_list = ["sentence_wiki.json", "sentence_baike.json", "sentence_news.json", "sentence_web.json"]

word_p = {}
f = open("../database/all_word.json", "r", encoding="gbk")
word_list = json.load(f)
f.close()
# 加一平滑
for word in word_list["all"]:
    word_p[word] = 1

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
        for i in range(len(sen)):
            if sen[i] in word_p:
                word_p[sen[i]] += 1

json_str = json.dumps(word_p, ensure_ascii=False)
with open('../database/numres/probability.json', 'w', encoding="utf-8") as json_file:
    json_file.write(json_str)
    