import json

file_list = ["sentence_wiki.json", "sentence_baike.json", "sentence_news.json", "sentence_web.json"]

def is_ch(uchar):
    """判断一个unicode是否是汉字"""
    if u'\u4e00' <= uchar  and uchar <= u'\u9fff':
        return True
    else:
        return False

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
        for i in range(0, len(sen) - 1):
            if (not is_ch(sen[i])) or (not is_ch(sen[i+1])):
                continue
            if sen[i] not in word_dict:
                word_dict[sen[i]] = {}
            if sen[i+1] not in word_dict[sen[i]]:
                word_dict[sen[i]][sen[i+1]] = 1
            else:
                word_dict[sen[i]][sen[i+1]] += 1

json_str = json.dumps(word_dict, ensure_ascii=False)
with open('../database/numres/transmission.json', 'w', encoding="utf-8") as json_file:
    json_file.write(json_str)
    