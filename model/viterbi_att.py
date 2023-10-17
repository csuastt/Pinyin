# 本程序: 实现基本维特比算法+注意力机制的程序
import sqlite3
import json
from math import log10

folder_path = "./database/"
# 使用的数据库
# db_name = "hmm_tables.db"
db_name = "hmm_tables_v1.1.db"
# wp_name = "word_probability.json"
wp_name = "word_probability_v2.json"
# 平滑参数
# alpha 
# alpha2 
# 注意力权重
# beta 
# gamma 
f = open(folder_path + "pinyin_word.json", "r", encoding="gbk")
py_word = json.load(f)
f.close()
f = open(folder_path + wp_name, "r", encoding="gbk")
word_p = json.load(f)
f.close()


def viter(pinyin_list, beta=0.03, gamma=0.93, alpha=0.5, alpha2=0.1):
    '''
    @brief 利用维特比算法计算拼音对应的汉字
    @param 拼音的列表(可能为空)
    @return 返回汉字的列表(可能为空)
    '''
    # 空拼音对应空汉字
    if len(pinyin_list) == 0:
        return []
    # 路径及dp字典
    word_path = {}
    dp = [{}, {}]
    # 连接数据库
    conn = sqlite3.connect(folder_path + db_name)
    cur = conn.cursor()
    # 处理开头字
    # 获取候选字
    candidates = py_word[pinyin_list[0]]
    # 查询数据库
    if len(pinyin_list) > 1:
        query_res = list(cur.execute('''SELECT EMISSION.WORD, STARTING.PROBABILITY, EMISSION.PROBABILITY, TRANSPYWORD.PROBABILITY
                                    FROM EMISSION
                                    LEFT JOIN STARTING 
                                    ON EMISSION.WORD = STARTING.WORD 
                                    LEFT JOIN TRANSPYWORD
                                    ON (EMISSION.WORD = TRANSPYWORD.PRE AND TRANSPYWORD.PINYIN = "{}")
                                    WHERE EMISSION.PINYIN = "{}" 
                                    '''.format(pinyin_list[0], pinyin_list[1])))
        for item in query_res:
            if item[0] in candidates:
                if item[1] is None:
                    str_val = 0
                else:
                    str_val = item[1]
                if item[3] is None:
                    att_val = 0
                else:
                    att_val = item[3]
                dp[0][item[0]] = -log10(alpha * 10 ** (-str_val) + \
                        alpha2 * 10 ** (-att_val) + (1-alpha-alpha2) * (10 ** -(word_p[item[0]]))) + item[2]
                word_path[item[0]] = [item[0]]
    else:
        query_res = list(cur.execute('''SELECT EMISSION.WORD, STARTING.PROBABILITY, EMISSION.PROBABILITY
                                    FROM EMISSION
                                    LEFT JOIN STARTING 
                                    ON STARTING.WORD = EMISSION.WORD
                                    WHERE EMISSION.PINYIN = "{}"
                                    '''.format(pinyin_list[0])))
        for item in query_res:
            if item[0] in candidates:
                if item[1] is None:
                    dp[0][item[0]] = -log10(1 - alpha) + word_p[item[0]] + item[2]
                else:
                    dp[0][item[0]] = -log10(alpha * (10 ** (-item[1])) + \
                        (1 - alpha) * (10 ** -(word_p[item[0]]))) + item[2]
                word_path[item[0]] = [item[0]]
    # 对开头没出现过的字进行零概率平滑
    for word in candidates:
        if word not in word_path.keys():
            dp[0][word] = -log10(1 - alpha) + word_p[word]
            word_path[word] = [word]

    # 处理后续字
    for i in range(1, len(pinyin_list)):
        py = pinyin_list[i]
        last_py = pinyin_list[i-1]
        ok_tranpy = False
        if ok_tranpy:
            next_py = pinyin_list[i+1]
        next_path = {}
        dp[i%2].clear()

        # 提取候选字
        candidates = py_word[py]
        emi_res = dict(cur.execute('''SELECT EMISSION.WORD, EMISSION.PROBABILITY
                                    FROM EMISSION
                                    WHERE EMISSION.PINYIN = "{}"
                                    '''.format(py)))
        tran_res = list(cur.execute('''SELECT TRANSMISSION.PRE, TRANSMISSION.REAR, TRANSMISSION.PROBABILITY
                        FROM TRANSMISSION
                        JOIN EMISSION
                        ON EMISSION.WORD = TRANSMISSION.PRE
                        JOIN EMISSION AS TMP
                        ON TMP.WORD = TRANSMISSION.REAR
                        WHERE EMISSION.PINYIN = "{}" AND TMP.PINYIN = "{}"'''.format(last_py, py)))
        if ok_tranpy:
            tranpy_res = dict(cur.execute('''SELECT TRANSPYWORD.PRE, TRANSPYWORD.PROBABILITY
                        FROM TRANSPYWORD
                        JOIN EMISSION
                        ON EMISSION.WORD = TRANSPYWORD.PRE
                        WHERE EMISSION.PINYIN = "{}" AND TRANSPYWORD.PINYIN = "{}"'''.format(py, next_py)))
        for rear in candidates:
            # 找到rear所有有关转移值
            tran_dict = {}
            for j in range(len(tran_res)):
                if tran_res[j][1] == rear:
                    tran_dict[tran_res[j][0]] = tran_res[j][2]
            if ok_tranpy and (rear in tranpy_res):
                tranpy_val = gamma * 10 ** (-tranpy_res[rear])
            else:
                tranpy_val = 0
            # 找到最优的转移
            best_p = 999999999
            best_pre = None
            for pre in word_path.keys():
                if pre in tran_dict.keys():
                    tran_val = beta * (10 ** (-tran_dict[pre]))
                else:
                    tran_val = 0
                prob = -log10(tran_val + tranpy_val + \
                        (1 - beta - gamma) * (10 ** -(word_p[rear]))) + \
                        dp[(i-1)%2][pre]
                if prob < best_p:
                    best_p = prob
                    best_pre = pre
            if rear in emi_res.keys():
                dp[i%2][rear] = best_p + emi_res[rear]
            else:
                dp[i%2][rear] = best_p
            next_path[rear] = word_path[best_pre] + [rear]
        # 更新路径
        word_path = next_path
    
    # 找出最佳的路径
    prob, state = min([(dp[(len(pinyin_list) - 1)%2][word], word) 
                        for word in word_path.keys()])
    return word_path[state]
