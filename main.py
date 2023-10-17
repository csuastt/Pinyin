# 本程序是测试入口
# from model.viterbi import viter
from model.viterbi_3 import viter
# from model.viterbi_att import viter
import sys
import time

if len(sys.argv) == 1:
    # 模式一: 无命令行参数(即"python main.py"), 直接在终端输入字符串
    while 1:
        str = input("请输入拼音: ")
        # 输入"q"或"exit"退出
        if str == 'q' or str == 'exit':
            break
        # 计时开始
        time_s = time.time()
        py_list = str.lower().split()
        word_path = viter(py_list)
        print("结果: " + "".join(word_path))
        print("耗时: %.2fs"%(time.time() - time_s))
elif len(sys.argv) == 4 or len(sys.argv) == 3:
    # 模式二: 指定输入输出文件路径
    # 第一位是输入文件路径
    # 第二位是输出文件路径
    # 第三位为编码格式, 默认utf-8, 可不输入
    input_f = sys.argv[1]
    output_f = sys.argv[2]

    if len(sys.argv) == 4:
        fin = open(input_f, "r", encoding=sys.argv[3])
        fout = open(output_f, "w", encoding=sys.argv[3])
    else:
        fin = open(input_f, "r", encoding="utf-8")
        fout = open(output_f, "w", encoding="utf-8")
    # 计时开始
    time_s = time.time()
    for line in fin.readlines():
        line = line.strip('\n')
        py_list = line.lower().split()
        word_path = viter(py_list)
        fout.write("".join(word_path) + '\n')
    print("耗时: %.2fs"%(time.time() - time_s))
    fin.close()
    fout.close()
else:
    # 模式三: 指定输入输出文件路径, 并与标准答案对比
    # 第一位是输入文件路径
    # 第二位是输出文件路径
    # 第三位是标准文件路径
    # 第四位是标志位, 请输入"1"
    # 第五位为编码格式, 默认utf-8, 可不输入
    input_f = sys.argv[1]
    output_f = sys.argv[2]
    std_f = sys.argv[3]

    if len(sys.argv) == 6:
        fin = open(input_f, "r", encoding=sys.argv[5])
        fout = open(output_f, "w", encoding=sys.argv[5])
        fstd = open(std_f, "r", encoding=sys.argv[5])
    else:
        fin = open(input_f, "r", encoding="utf-8")
        fout = open(output_f, "w", encoding="utf-8")
        fstd = open(std_f, "r", encoding="utf-8")

    # 计时开始
    time_s = time.time()

    inp = list(fin.readlines())
    std = list(fstd.readlines())
    tot_sen = len(inp)
    right_sen = 0
    tot_word = 0
    right_word = 0

    for i in range(len(inp)):
        py_list = inp[i].strip('\n').lower().split()
        std_str = std[i].strip('\n')
        word_path = viter(py_list)
        word_str = "".join(word_path)
        fout.write(word_str + '\n')
        # 与标准比较
        all_ok = True
        for i in range(len(word_str)):
            if word_str[i] == std_str[i]:
                right_word += 1
            else:
                all_ok = False
            tot_word += 1
        if (all_ok):
            right_sen += 1

    # 打印正确率
    print("字正确率: %.4f"%(right_word/tot_word))
    print("句正确率: %.4f"%(right_sen/tot_sen))
    print("耗时: %.2fs"%(time.time() - time_s))

    fin.close()
    fout.close()
    fstd.close()
