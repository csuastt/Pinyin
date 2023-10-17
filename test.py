# 本程序是调参程序
from matplotlib import pyplot as plt
import numpy as np
# from model.viterbi import viter
# from model.viterbi_3 import viter
from model.viterbi_att import viter
import sys
# 载入画图模块
# 载入模块
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import seaborn as sns
from scipy import interpolate

# 功能函数
def plot3D(x, y, z, x_label, y_label, z_label):
    #插值
    f = interpolate.interp2d(x, y, z, kind='linear')
    xnew = x
    ynew = y
    znew = f(xnew, ynew)

    #修改x,y，z输入画图函数前的shape
    xx1, yy1 = np.meshgrid(xnew, ynew)
    newshape = (xx1.shape[0])*(xx1.shape[0])
    y_input = xx1.reshape(newshape)
    x_input = yy1.reshape(newshape)
    z_input = znew.reshape(newshape)

    #画图
    sns.set(style='white')
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(x_input,y_input,z_input,cmap=cm.coolwarm)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)
    ax.set_zlim([0,1])
    plt.show()

# 一元还是二元调参
num_param = 2

if num_param == 1:
    # 一元调参
    # 需要测试的参数列表
    params = [i/100 for i in range(90,100)]
    params_label = "Beta"
    # 结果
    word_x = []
    word_y = []
    sen_x = []
    sen_y = []

    for param in params:
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

        inp = list(fin.readlines())
        std = list(fstd.readlines())
        tot_sen = len(inp)
        right_sen = 0
        tot_word = 0
        right_word = 0

        for i in range(len(inp)):
            py_list = inp[i].strip('\n').lower().split()
            std_str = std[i].strip('\n')
            word_path = viter(py_list, beta=param)
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
        sen_x.append(param)
        sen_y.append(right_sen/tot_sen)
        word_x.append(param)
        word_y.append(right_word/tot_word)

        fin.close()
        fout.close()
        fstd.close()
    # 作图可视化
    plt.plot(sen_x, sen_y, '-', label='Sentence')
    plt.plot(word_x, word_y, '-', label='Word')
    plt.ylabel("Accuracy")
    plt.xlabel(params_label)
    plt.legend()
    plt.show()
else:
    # 二元调参
    # 需要测试的参数列表
    params1 = [i/100 for i in range(0,100,5)]
    params2 = [i/100 for i in range(0,100,5)]
    params1_label = "Beta"
    params2_label = "Gamma"
    # 结果
    word_x = []
    word_y = []
    word_z = []
    sen_x = []
    sen_y = []
    sen_z = []

    for param1 in params1:
        for param2 in params2:
            if param1 + param2 >= 1.0:
                continue
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

            inp = list(fin.readlines())
            std = list(fstd.readlines())
            tot_sen = len(inp)
            right_sen = 0
            tot_word = 0
            right_word = 0

            for i in range(len(inp)):
                py_list = inp[i].strip('\n').lower().split()
                std_str = std[i].strip('\n')
                word_path = viter(py_list, beta=param1, gamma=param2)
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
            sen_x.append(param1)
            sen_y.append(param2)
            sen_z.append(right_sen/tot_sen)
            word_x.append(param1)
            word_y.append(param2)
            word_z.append(right_word/tot_word)

            fin.close()
            fout.close()
            fstd.close()
    # 作图可视化
    plot3D(sen_x, sen_y, sen_z, params1_label, params2_label, 'Sentence Accuracy')
    plot3D(word_x, word_y, word_z, params1_label, params2_label, 'Word Accuracy')
    # X = np.zeros((4,4))
    # plt.imshow(X,cmap=plt.cm.hot, vmin=0, vmax=1, interpolation="mitchell")
