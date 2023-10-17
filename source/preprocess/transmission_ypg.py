import json
import sqlite3
from math import log10
import pickle

# 所有汉字的全集
f = open("../database/all_word.json", "r", encoding="gbk")
all_word = json.load(f)
all_word = set(all_word["all"])
f.close()

# 读取数据库
# 打开数据库文件
file_path = "hmm_tables_v2.db"
conn = sqlite3.connect("../database/" + file_path)
# 获取游标
cur = conn.cursor()

# index
with open("../database/ypg/index.json", "r", encoding="utf-8") as f:
    index = json.load(f)

# dic
with open("../database/ypg/gram.pkl", "rb") as f:
    raw_dict = pickle.load(f)

# 写入数据库
# cur.execute('''CREATE TABLE TRANSMISSION
#     (ID INT PRIMARY KEY     NOT NULL,
#     PRE           STRING(1)  NOT NULL,
#     REAR          STRING(1)  NOT NULL,
#     PROBABILITY       FLOAT     NOT NULL
#     );''')
# i = 0

# # 2-gram
# word_dict = raw_dict["z2z"]
# for pre in word_dict.keys():
#     if index["i2z"][pre] not in all_word:
#         continue
#     for rear in word_dict[pre].keys():
#         if index["i2z"][rear] not in all_word:
#             continue
#         cur.execute('INSERT INTO TRANSMISSION (ID,PRE,REAR,PROBABILITY) \
#             VALUES ({}, "{}", "{}", {})'.format(i, index["i2z"][pre], index["i2z"][rear], -log10(word_dict[pre][rear])))
#         i += 1
# conn.commit()


# 3-gram
cur.execute('''CREATE TABLE TRANSMISSION3
    (ID INT PRIMARY KEY     NOT NULL,
    PPRE           STRING(1)  NOT NULL,
    PRE           STRING(1)  NOT NULL,
    REAR          STRING(1)  NOT NULL,
    PROBABILITY       FLOAT     NOT NULL
    );''')
i = 0
word_dict = raw_dict["z3z"]    
for pre in word_dict.keys():
    if (index["i2z"][pre[0]] not in all_word) or \
        (index["i2z"][pre[1]] not in all_word):
        continue
    for rear in word_dict[pre].keys():
        if index["i2z"][rear] not in all_word:
            continue
        cur.execute('INSERT INTO TRANSMISSION3 (ID,PPRE,PRE,REAR,PROBABILITY) \
            VALUES ({}, "{}", "{}", "{}", {})'.format(i, index["i2z"][pre[0]], index["i2z"][pre[1]], index["i2z"][rear], -log10(word_dict[pre][rear])))
        i += 1
        if not (i % 10000):
            print(i)
conn.commit()
conn.close()