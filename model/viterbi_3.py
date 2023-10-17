# 本程序: 实现基本维特比算法的程序
import sqlite3
import json
from math import log10

folder_path = "./database/"
# 使用的数据库
db_name = "hmm_tables_v2.db"
wp_name = "word_probability_v2.json"
# 平滑参数
# alpha = 0.9
# # 二元三元的比例参数
# beta2 = 0.09
# beta3 = 0.9
f = open(folder_path + "pinyin_word.json", "r", encoding="gbk")
py_word = json.load(f)
f.close()
f = open(folder_path + wp_name, "r", encoding="gbk")
word_p = json.load(f)
f.close()


def viter(pinyin_list, alpha=0.9, beta2 = 0.09, beta3=0.9, lamb=1):
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
    query_res = cur.execute('''SELECT EMISSION.WORD, STARTING.PROBABILITY, EMISSION.PROBABILITY
                                FROM EMISSION
                                LEFT JOIN STARTING 
                                ON STARTING.WORD = EMISSION.WORD
                                WHERE EMISSION.PINYIN = "{}"
                                '''.format(pinyin_list[0]))
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
        next_path = {}
        dp[i%2].clear()

        # 提取候选字
        candidates = py_word[py]
        # 查询数据库
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
                        WHERE EMISSION.PINYIN = "{}" AND TMP.PINYIN = "{}"'''.format(pinyin_list[i-1], py)))
        if i > 1:
            tran3_res = list(cur.execute('''SELECT TRANSMISSION3.PPRE, TRANSMISSION3.PRE, TRANSMISSION3.REAR, TRANSMISSION3.PROBABILITY
                            FROM TRANSMISSION3
                            JOIN EMISSION
                            ON EMISSION.WORD = TRANSMISSION3.PPRE
                            JOIN EMISSION AS TMP1
                            ON TMP1.WORD = TRANSMISSION3.PRE
                            JOIN EMISSION AS TMP2
                            ON TMP2.WORD = TRANSMISSION3.REAR
                            WHERE EMISSION.PINYIN = "{}" AND TMP1.PINYIN = "{}" AND TMP2.PINYIN = "{}"
                                '''.format(pinyin_list[i-2], pinyin_list[i-1], py)))

        for rear in candidates:
            # 找到rear所有有关转移值
            tran_dict = {}
            for j in range(len(tran_res)):
                if tran_res[j][1] == rear:
                    tran_dict[tran_res[j][0]] = tran_res[j][2]
            if i > 1:
                tran3_dict = {}
                for j in range(len(tran3_res)):
                    if tran3_res[j][2] == rear:
                        tran3_dict[tran3_res[j][0]+tran3_res[j][1]] = tran3_res[j][3]

            best_p = 999999999
            best_pre = None
            for pre in word_path.keys():
                if pre in tran_dict:
                    tran_val = beta2 * (10 ** (-tran_dict[pre]))
                else:
                    tran_val = 0
                if i > 1 and (word_path[pre][len(word_path[pre])-2]+pre) in tran3_dict:
                    tran3_val = beta3 * (10 ** (-tran3_dict[word_path[pre][len(word_path[pre])-2]+pre]))
                else:
                    tran3_val = 0
                prob = -log10(tran_val + tran3_val + \
                        (1 - beta2 - beta3) * (10 ** -(word_p[rear]))) + \
                        dp[(i-1)%2][pre]
                if prob < best_p:
                    best_p = prob
                    best_pre = pre
            if rear in emi_res.keys():
                dp[i%2][rear] = best_p + lamb * emi_res[rear]
            else:
                dp[i%2][rear] = best_p
            next_path[rear] = word_path[best_pre] + [rear]
        # 更新路径
        word_path = next_path
    
    # 找出最佳的路径
    prob, state = min([(dp[(len(pinyin_list) - 1)%2][word], word) 
                        for word in word_path.keys()])
    return word_path[state]
