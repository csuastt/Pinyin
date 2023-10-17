# 本程序: 分析语料库, 生成HMM的三个矩阵, 并写入数据库; 计算每个字出现的概率
import sqlite3
import json
from math import log10
from pypinyin import pinyin, Style

f = open("../database/all_sentence.json", "r", encoding="gbk")
sentence_list = json.load(f)
f.close()


def init(file_path):
    # 打开数据库文件
    conn = sqlite3.connect("../database/" + file_path)
    # 获取游标
    cur = conn.cursor()
    return conn, cur


def build_starting(conn, cur):
    '''
    建立初值概率矩阵
    '''
    word_dict = {}
    # 计算句首字的概率
    for sen in sentence_list["all"]:
        if not len(sen):
            continue
        if pinyin(sen[0], style=Style.NORMAL,errors=lambda x: '*')[0][0] == '*':
            continue
        if sen[0] not in word_dict:
            word_dict[sen[0]] = 1
        else:
            word_dict[sen[0]] += 1
    for key in word_dict.keys():
        word_dict[key] = -log10(word_dict[key]/len(sentence_list["all"]))
    # 写入数据库
    cur.execute('''CREATE TABLE STARTING
        (ID INT PRIMARY KEY     NOT NULL,
        WORD           STRING(1)  NOT NULL,
        PROBABILITY       FLOAT     NOT NULL
        );''')
    i = 0
    for key in word_dict.keys():
        if key == '"':
            continue
        cur.execute('INSERT INTO STARTING (ID,WORD,PROBABILITY) \
            VALUES ({}, "{}", {})'.format(i, key, word_dict[key]))
        i += 1
    conn.commit()


def build_transmission(conn, cur):
    '''
    建立转移概率矩阵, 已知某个字符, 问下一个字符的概率
    '''
    word_dict = {}
    # 计算二元关系转移矩阵
    k = 1
    for sen in sentence_list["all"]:
        print("%d / %d"%(k, len(sentence_list["all"])))
        k += 1
        if not len(sen):
            continue
        for i in range(0, len(sen) - 1):
            if pinyin(sen[i], style=Style.NORMAL,errors=lambda x: '*')[0][0] == '*' or \
                pinyin(sen[i+1], style=Style.NORMAL,errors=lambda x: '*')[0][0] == '*':
                continue
            if sen[i] not in word_dict:
                word_dict[sen[i]] = {}
            if sen[i+1] not in word_dict[sen[i]]:
                word_dict[sen[i]][sen[i+1]] = 1
            else:
                word_dict[sen[i]][sen[i+1]] += 1
    for pre in word_dict.keys():
        cnt = 0
        for rear in word_dict[pre].keys():
            cnt += word_dict[pre][rear]
        for rear in word_dict[pre].keys():
            word_dict[pre][rear] = -log10((word_dict[pre][rear]/cnt))
    # 写入数据库
    cur.execute('''CREATE TABLE TRANSMISSION
        (ID INT PRIMARY KEY     NOT NULL,
        PRE           STRING(1)  NOT NULL,
        REAR          STRING(1)  NOT NULL,
        PROBABILITY       FLOAT     NOT NULL
        );''')
    i = 0
    for pre in word_dict.keys():
        for rear in word_dict[pre].keys():
            if pre == '"' or rear == '"':
                continue
            cur.execute('INSERT INTO TRANSMISSION (ID,PRE,REAR,PROBABILITY) \
                VALUES ({}, "{}", "{}", {})'.format(i, pre, rear, word_dict[pre][rear]))
            i += 1
    conn.commit()


def build_emission(conn, cur):
    '''
    建立发射概率矩阵
    '''
    word_dict = {}
    # 计算每个字的各个发音的概率
    k = 1
    for sen in sentence_list["all"]:
        print("%d / %d"%(k, len(sentence_list["all"])))
        k += 1
        if not len(sen):
            continue
        sen_pinyin = pinyin(sen, style=Style.NORMAL,errors=lambda x: len(x)*['*'])
        for i in range(len(sen)):
            # 跳过没有拼音的字符
            if sen_pinyin[i][0] == '*':
                continue
            if sen[i] not in word_dict:
                word_dict[sen[i]] = {}
            if sen_pinyin[i][0] not in word_dict[sen[i]]:
                word_dict[sen[i]][sen_pinyin[i][0]] = 1
            else:
                word_dict[sen[i]][sen_pinyin[i][0]] += 1
    for word in word_dict.keys():
        cnt = 0
        for py in word_dict[word].keys():
            cnt += word_dict[word][py]
        for py in word_dict[word].keys():
            word_dict[word][py] = -log10((word_dict[word][py]/cnt))
    # 写入数据库
    cur.execute('''CREATE TABLE EMISSION
        (ID INT PRIMARY KEY     NOT NULL,
        WORD           STRING(1)  NOT NULL,
        PINYIN         STRING(8)  NOT NULL,
        PROBABILITY       FLOAT     NOT NULL
        );''')
    i = 0
    for word in word_dict.keys():
        for py in word_dict[word].keys():
            cur.execute('INSERT INTO EMISSION (ID,WORD,PINYIN,PROBABILITY) \
                VALUES ({}, "{}", "{}", {})'.format(i, word, py, word_dict[word][py]))
            i += 1
    conn.commit()


def build_word_p():
    '''
    计算每个字出现的概率。
    为了避免0概率，统一采用加一平滑。
    '''
    word_p = {}
    # 读入所有可能的字
    f = open("../database/all_word.json", "r", encoding="gbk")
    word_list = json.load(f)
    f.close()
    # 加一平滑
    for word in word_list["all"]:
        word_p[word] = 1
    # 计算每个字产生的概率
    k = 1
    for sen in sentence_list["all"]:
        print("%d / %d"%(k, len(sentence_list["all"])))
        k += 1
        if not len(sen):
            continue
        for i in range(len(sen)):
            if sen[i] in word_p:
                word_p[sen[i]] += 1
    # 计算概率
    cnt = 0
    for word in word_p.keys():
        cnt += word_p[word]
    for word in word_p.keys():
        word_p[word] = -log10((word_p[word]/cnt))
    # 存储
    json_str = json.dumps(word_p, ensure_ascii=False)
    with open('../database/word_probability.json', 'w', encoding="gbk") as json_file:
        json_file.write(json_str)


def main():
    '''
    程序入口
    '''
    conn, cur = init("hmm_tables.db")
    # build_starting(conn, cur)
    # build_transmission(conn, cur)
    # build_emission(conn, cur)
    build_word_p()
    conn.close()


main()
