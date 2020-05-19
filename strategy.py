# -*- coding:utf-8 -*-
from pyhanlp import HanLP
import pandas as pd
import random
from collections import defaultdict
import re
class TrieNode(object):
    def __init__(self, value=None):
        # 值
        self.value = value
        # fail指针
        self.fail = None
        # 尾标志：标志为i表示第i个模式串串尾，默认为0
        self.tail = 0
        # 子节点，{value:TrieNode}
        self.children = {}

class Trie(object):
    def __init__(self, words):
        # print("初始化")
        # 根节点
        self.root = TrieNode()
        # 模式串个数
        self.count = 0
        self.words = words
        for word in words:
            self.insert(word)
        self.ac_automation()
        # print("初始化完毕")

    def insert(self, sequence):
        """
        基操，插入一个字符串
        :param sequence: 字符串
        :return:
        """
        self.count += 1
        cur_node = self.root

        if type(sequence)!=str:
            sequence=str(sequence)
        for item in sequence:
            if item not in cur_node.children:
                # 插入结点
                child = TrieNode(value=item)
                cur_node.children[item] = child
                cur_node = child
            else:
                cur_node = cur_node.children[item]
        cur_node.tail = self.count

    def ac_automation(self):
        """
        构建失败路径
        :return:
        """
        queue = [self.root]
        # BFS遍历字典树
        while len(queue):
            temp_node = queue[0]
            # 取出队首元素
            queue.remove(temp_node)
            for value in temp_node.children.values():
                # 根的子结点fail指向根自己
                if temp_node == self.root:
                    value.fail = self.root
                else:
                    # 转到fail指针
                    p = temp_node.fail
                    while p:
                        # 若结点值在该结点的子结点中，则将fail指向该结点的对应子结点
                        if value.value in p.children:
                            value.fail = p.children[value.value]
                            break
                        # 转到fail指针继续回溯
                        p = p.fail
                    # 若为None，表示当前结点值在之前都没出现过，则其fail指向根结点
                    if not p:
                        value.fail = self.root
                # 将当前结点的所有子结点加到队列中
                queue.append(value)

    def search(self, text):
        """
        模式匹配
        :param self:
        :param text: 长文本
        :return:
        """
        p = self.root
        # 记录匹配起始位置下标
        start_index = 0
        # 成功匹配结果集
        rst = defaultdict(list)
        for i in range(len(text)):
            single_char = text[i]
            while single_char not in p.children and p is not self.root:
                p = p.fail
            # 有一点瑕疵，原因在于匹配子串的时候，若字符串中部分字符由两个匹配词组成，此时后一个词的前缀下标不会更新
            # 这是由于KMP算法本身导致的，目前与下文循环寻找所有匹配词存在冲突
            # 但是问题不大，因为其标记的位置均为匹配成功的字符
            if single_char in p.children and p is self.root:
                start_index = i
            # 若找到匹配成功的字符结点，则指向那个结点，否则指向根结点
            if single_char in p.children:
                p = p.children[single_char]
            else:
                start_index = i
                p = self.root
            temp = p
            while temp is not self.root:
                # 尾标志为0不处理，但是tail需要-1从而与敏感词字典下标一致
                # 循环原因在于，有些词本身只是另一个词的后缀，也需要辨识出来
                if temp.tail:
                    rst[self.words[temp.tail - 1]].append((start_index, i))
                temp = temp.fail
        return rst

def direct_search(test_text):
    # 并行检索
    # 策略1:直接量化。优先“汉语情感词极值表.txt”，然后“情感词汇本体.xlsx”；
    #1.1
    mode = []
    pro_df1 = pd.read_csv('dict_res/jizhi_first.csv',encoding='utf-8')
    words1 = list(pro_df1['word'])
    model_fir = Trie(words1)

    temp1 = model_fir.search(test_text)
    for i in list(model_fir.search(test_text).keys()):
        temp1[i] = [temp1[i][0],float(pro_df1.loc[pro_df1['word']==i,['value']].sum())]
    mode.append(temp1)
    #1.2
    pro_df2 = pd.read_csv('dict_res/jizhi_second.csv',encoding='utf-8')
    words2 = list(pro_df2['word'])
    model_sec = Trie(words2)

    temp2 = model_sec.search(test_text)
    for i in list(model_sec.search(test_text).keys()):
        temp2[i] = [temp2[i][0],float(pro_df2.loc[pro_df2['word']==i,['value']].sum())]
    mode.append(temp2)

    return temp1, temp2

def indirect_search(test_text):
    # 策略2:间接量化。再然后总表“negtive_all.txt”和“positive_all.txt”；
    # 2.1消极
    neg_dict = open('dict_res/negtive_all.txt', encoding='utf-8').read().split('\n')
    model_th = Trie(neg_dict)

    temp3 = model_th.search(test_text)
    for i in list(model_th.search(test_text).keys()):
        temp3[i] = [temp3[i][0], -2.5]

    # 2.2积极
    pos_dict = open('dict_res/positive_all.txt', encoding='utf-8').read().split('\n')
    model_fo = Trie(pos_dict)

    temp4 = model_fo.search(test_text)
    for i in list(model_fo.search(test_text).keys()):
        temp4[i] = [temp4[i][0], 2.5]

    temp_res = work_bn(temp4,temp3)

    return temp_res

def remove(test_text):
    a = HanLP.segment(test_text)
    rem = dict()
    curs = 0
    for i in a:
        if str(i.nature) in ['ns','nz']:
            rem[str(i.word)] = [(curs,curs+len(str(i.word))-1)]
        curs += len(str(i.word))

    return rem

def result_correct(test_text):
    # 策略3:修正。情绪修饰词的权重，正向表“程度级别.txt”和反向表“否定.txt”
    modify = dict()
    weight_dict = {'极其': 1.9, '很': 1.7, '超': 1.5,'较': 0.9, '稍': 0.7, '欠': 0.5, '否定': -0.9}
    for i in list(weight_dict.keys()):
        weight = open('dict_res/{}.txt'.format(i), encoding='utf-8').read().split('\n')
        # print(weight)
        model_add = Trie(weight).search(test_text)
        if model_add:
            for spe in model_add.keys():
                modify[spe] = [model_add[spe][0],weight_dict[i]]

    return modify

#位置词归一化
def work_bn(base,accord):#base是短而错，accord是长而对
    temp_res = dict(base)
    if accord and base:
        for i, j in base.items():
            for m in accord.values():

                if j[0][0] >= m[0][0] and j[0][1] <= m[0][1]:
                    try:
                        temp_res.pop(i)
                    except:
                        print(temp_res,i)
    # 积极/消极归一
    temp_res.update(accord)
    return temp_res

def bn_march(test_text):
    direct = direct_search(test_text)
    indirect = indirect_search(test_text)

    rem = remove(test_text)

    # 积/消极词与极性值归一
    direct1, direct2 = direct
    res1 = dict()
    # 剔乱码
    if direct1:
        direct1 = work_bn(direct1, indirect)
        direct1 = work_bn(direct1, rem)
    # 剔地址
    for i in direct1.keys():
        if i not in rem.keys():
            res1[i] = direct1[i]

    res2 = dict()
    if direct2:
        direct2 = work_bn(direct2, indirect)
        direct2 = work_bn(direct2, rem)
    for i in direct2.keys():
        if i not in rem.keys():
            res2[i] = direct2[i]

    return res1,res2

def weight(test_text,μ):
    res1, res2 = bn_march(test_text)
    res_final = dict()
    # 1,并集部分（已去交）
    # first词本结果
    spec1 = set(res1.keys()) - set(res2.keys())
    for i in list(spec1):
        res_final[i] = res1[i]
    # second词本结果
    spec2 = set(res2.keys()) - set(res1.keys())
    for i in list(spec2):
        res_final[i] = res2[i]

    # 2,交集部分结果加权平均得结果
    spec3 = set(res1.keys()) & set(res2.keys())
    for i in list(spec3):
        res_final[i] = [res1[i],res1[i][1] * μ + res2[i][1]* (1 - μ)]

    return res_final
def combine(test_text,μ=0.9):

    test_text = test_text[test_text.find(':')+1:]
    test_text = ','.join(re.compile(r'[\u4e00-\u9fa5]+').findall(test_text))

    correct = result_correct(test_text)

    res = weight(test_text,μ)

    res_update = res.copy()
    score = 0
    for i1,i2 in correct.items():
        sig = False
        for j1,j2 in res.items():

            try:
                j2[0][0] - i2[0][1]
            except:
                j2 = j2[0]
            if j2[0][0] - i2[0][1]<3:
                res_update[j1][1] = j2[1] * i2[1]
                sig = True
            else:
                pass
            if sig:
                break
    for i in res_update.values():
        score += i[1]

    if score>5:
        score=5
    elif score<-5:
        score=-5
    elif -1<score<1:
        score=(random.random()-0.5)*2

    return score

#不,-0.35529151896253897

if __name__ == "__main__":
    test_text = "合肥求拼！！江浙沪皖很讨厌！！"
    a = pd.read_csv('yuqing.csv',encoding='utf-8')
    a['score'] = a['comment_content'].apply(combine)
    print(a.head(5))
