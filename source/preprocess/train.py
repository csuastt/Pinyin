# 本程序: 分析语料库, 生成HMM的三个矩阵, 并写入数据库; 计算每个字出现的概率
import sqlite3
import json
from math import log10
from typing import KeysView
from pypinyin import pinyin, Style

# 所有汉字的全集
f = open("../database/all_word.json", "r", encoding="gbk")
all_word = json.load(f)
all_word = set(all_word["all"])
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
    f = open("../database/numres/starting.json", "r")
    word_dict = json.load(f)
    f.close()
    cnt = 0
    for key in word_dict.keys():
        if key in all_word:
            cnt += word_dict[key]
    for key in word_dict.keys():
        if key in all_word:
            word_dict[key] = -log10(word_dict[key]/cnt)
    # 写入数据库
    cur.execute('''CREATE TABLE STARTING
        (ID INT PRIMARY KEY     NOT NULL,
        WORD           STRING(1)  NOT NULL,
        PROBABILITY       FLOAT     NOT NULL
        );''')
    i = 0
    for key in word_dict.keys():
        if key in all_word:
            cur.execute('INSERT INTO STARTING (ID,WORD,PROBABILITY) \
            VALUES ({}, "{}", {})'.format(i, key, word_dict[key]))
            i += 1
    conn.commit()


def build_transmission(conn, cur):
    '''
    建立转移概率矩阵, 已知某个字符, 问下一个字符的概率
    '''
    f = open("../database/numres/transmission.json", "r")
    word_dict = json.load(f)
    f.close()
    # 统计概率
    for pre in word_dict.keys():
        if pre not in all_word:
            continue
        cnt = 0
        for rear in word_dict[pre].keys():
            if rear in all_word:
                cnt += word_dict[pre][rear]
        for rear in word_dict[pre].keys():
            if rear in all_word:
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
        if pre not in all_word:
            continue
        for rear in word_dict[pre].keys():
            if rear not in all_word:
                continue
            cur.execute('INSERT INTO TRANSMISSION (ID,PRE,REAR,PROBABILITY) \
                VALUES ({}, "{}", "{}", {})'.format(i, pre, rear, word_dict[pre][rear]))
            i += 1
    conn.commit()


def build_emission(conn, cur):
    '''
    建立发射概率矩阵
    '''
    f = open("../database/numres/emission.json", "r")
    word_dict = json.load(f)
    f.close()
    for word in word_dict.keys():
        if word not in all_word:
            continue
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
        if word not in all_word:
            continue
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
    f = open("../database/numres/probability.json", "r")
    word_p = json.load(f)
    f.close()
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


def build_trans_py_word(cur, conn):
    f = open("../database/numres/trans_py_word.json", "r")
    word_dict = json.load(f)
    f.close()
    # 统计概率
    for pre in word_dict.keys():
        cnt = 0
        for rear in word_dict[pre].keys():
            if rear in all_word:
                cnt += word_dict[pre][rear]
        for rear in word_dict[pre].keys():
            if rear in all_word:
                word_dict[pre][rear] = -log10((word_dict[pre][rear]/cnt))
    # 写入数据库
    # cur.execute('''CREATE TABLE TRANSPYWORD
    #     (ID INT PRIMARY KEY     NOT NULL,
    #     PINYIN           STRING(8)  NOT NULL,
    #     PRE          STRING(1)  NOT NULL,
    #     PROBABILITY       FLOAT     NOT NULL
    #     );''')
    i = 0
    for pre in word_dict.keys():
        for rear in word_dict[pre].keys():
            if rear not in all_word:
                continue
            cur.execute('INSERT INTO TRANSPYWORD (ID,PINYIN,PRE,PROBABILITY) \
                VALUES ({}, "{}", "{}", {})'.format(i, pre, rear, word_dict[pre][rear]))
            i += 1
    conn.commit()


def main():
    '''
    程序入口
    '''
    conn, cur = init("hmm_tables_v2.db")
    # build_starting(conn, cur)
    # build_transmission(conn, cur)
    # build_emission(conn, cur)
    # build_word_p()
    build_trans_py_word(cur, conn)
    conn.close()


main()
