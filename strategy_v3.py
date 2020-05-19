from pyhanlp import HanLP
import pandas as pd
import re
import random
import datetime
import warnings
import time
import redis
import jieba.analyse as analyse
warnings.filterwarnings('ignore')

from clickhouse_driver import Client
import json
import os
import urllib.request

# 1、构建url
# 2、构建一下请求头部
def bobao(content):
    #情感分析机器人
    url = 'https://oapi.dingtalk.com/robot/send?access_token=09ac4be869c6be7f1c640d9b450a9b288d6b37a779cff53fe7a6eb613e0536de'
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    # 3、构建请求数据
    data = {
        "msgtype": "text",
        "text": {"content": content},
        "at": {
             "atMobiles": [
                 False
             ],
             "isAtAll": False
         }  # @全体成员（在此可设置@特定某人）
    }
    # 4、对请求的数据进行json封装
    sendData = json.dumps(data)  # 将字典类型数据转化为json格式
    sendData = sendData.encode("utf-8")  # python3的Request要求data为byte类型

    # 5、发送请求
    request = urllib.request.Request(url=url, data=sendData, headers=header)

    # 6、将请求发回的数据构建成为文件格式

    opener = urllib.request.urlopen(request)
    # 7、打印返回的结果
    print(opener.read())

'''clickhouse数据库连接'''
client2 = Client(host='10.228.83.251',port = '19000', user='default', database='putao', password='nEB7+b3X')

'''redis链接'''
redis_pool = redis.ConnectionPool(host='10.228.83.85', port=6379, decode_responses=True)
redis_conn = redis.Redis(connection_pool=redis_pool)

def dict_join(comment_list):
    res = 0
    miu = 0
    temp1 = 0
    #1,程度词典
    miu_all = dict()
    weight_dict = {'extremely': 1.9, 'very': 1.7, 'exceed': 1.5, 'relative': 0.9, 'slight': 0.7, 'owe': 0.5, 'not': -0.9}
    for i in list(weight_dict.keys()):
        weight = open('dict_res/{}.txt'.format(i), encoding='utf-8').read().split('\n')
        for j in comment_list:
            if j in weight:
                miu_all[j] = weight_dict[i]

    if miu_all:
        miu = sum(miu_all.values())/len(miu_all.values())

    #2，极值词典一、二
    pro_df1 = pd.read_csv('dict_res/jizhi_first.csv',encoding='utf-8')
    pro_df2 = pd.read_csv('dict_res/jizhi_second.csv',encoding='utf-8')
    baselist1 = []
    for i in comment_list:
        base1 = pro_df1.loc[pro_df1['word'] == i,['value']].sum()
        baselist1.append(float(base1))
        base2 = pro_df2.loc[pro_df2['word'] == i, ['value']].sum()
        baselist1.append(float(base2))
    #归一化

    if baselist1:
        temp1 = abs(max(baselist1))+abs(min(baselist1))
    #定正负
    if sum(baselist1)>0:
        base_f1 = temp1
    else:
        base_f1= -temp1
    #3,积/消极词典
    neg_count = 0
    pos_count = 0
    neg_dict = open('dict_res/negtive_all.txt', encoding='utf-8').read().split('\n')
    pos_dict = open('dict_res/positive_all.txt', encoding='utf-8').read().split('\n')
    for i in comment_list:
        if i in neg_dict:
            neg_count += 1
        else:
            pos_count += 1

    if abs(miu*base_f1)>1:
        if pos_count>=neg_count:
            res = abs(miu*base_f1)
        else:
            res = -abs(miu * base_f1)
    else:
        if (not neg_count) & (not pos_count):
            res = 2*random.random()
        else:
            res = 4 *random.random() * (pos_count - neg_count) / (neg_count + pos_count)

    return res

def clean(inp_text):
    text =str(inp_text)
    #1，加载停用词
    stop_dict = open('dict_res/HIT_stop_words.txt',encoding='utf-8').read().split('\n')
    #2，取中文
    text = text[text.find(':')+1:]
    text = ','.join(re.compile(r'[\u4e00-\u9fa5]+').findall(text))
    #3，分词去停用词

    text_update = []
    a = HanLP.segment(text)

    for i in a:

        if (str(i.word) not in stop_dict) and (str(i.nature) not in ['ns']):
            text_update.append(i.word)

    return text_update

def get_score(text):
    comment_list = clean(text)
    res = dict_join(comment_list)
    if abs(res)>=4.9:
        res = 4*res/(abs(int(res))+1)#平滑
    elif abs(res)<=1:
        res = 2*res

    return round(res,2)

# topic，version1
# select platform_cid,blog_id,blog_content from putao.f_weibo_blog where DATEDIFF(hh,NOW(),publish_time)<7 limit 1000
def siglerow(text, keyword_num=1):
    text = text[text.find(':') + 1:]
    text = ','.join(re.compile(r'[\u4e00-\u9fa5]+').findall(text))
    kw1 = analyse.textrank(text,keyword_num,allowPOS=('ns','n','vn','b'))
    kw2 = HanLP.extractKeyword(text,1)

    k_words = HanLP.segment(text)
    kw3 = ''
    for i in k_words:
        if str(i.nature)[0] == 'n':
            kw3 = str(i.word)
            break
    kw4 = analyse.textrank(text,keyword_num)

    if kw1:
        return str(kw1[0])  # jieba关键词，仅限于地点，名词，动名词
    elif kw2:
        return str(kw2[0]) # hanlp关键词
    elif kw3:
        return kw3 # 仅限于地点，名词，动名词
    elif kw4:
        return str(kw4[0])
    else:
        return ''


if __name__ =="__main__":
    data_set_name = 'jiankong_fenxi'
    sc_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_zhixing = '程序开始执行  执行时间%s!' % (sc_time)
    bobao(content=start_zhixing)
    click_house = client2.execute("select * from putao.f_weibo_blog_comment where comment_time>='2020-02-17 00:00:00' limit 10", types_check=True)
    col = client2.execute('DESCRIBE TABLE putao.f_weibo_blog_comment')
    col = pd.DataFrame(col)
    data = pd.DataFrame(click_house,columns=col[0].tolist())

    data_list = [data.ix[i].to_dict() for i in data.index.values]
    data_li = []
    data_limit = 2
    count = 0
    for i in data_list:
        msg_name = str(i)
        producte = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if redis_conn.sismember(data_set_name,msg_name):
            continue
        else:
            redis_conn.sadd(data_set_name,msg_name)
        count+=1

        score = get_score(i['comment_content'])
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        extract_words = siglerow(i['comment_content'])
        dict_aa = [{'comment_id':i['comment_id'],'keyword':extract_words,'score':score,'update_time':update_time}]
        data_frame = pd.DataFrame(dict_aa)
        data_li.append(data_frame)
            #批量入库
        if len(data_li) >= data_limit:
            for data_frame in data_li:
                data_frame = data_frame.values.tolist()
                print(data_frame)
                client2.execute('INSERT INTO f_weibo_blog_comment_an VALUES', data_frame, types_check=True)
            data_li = []
    if len(data_li) >= 0:
        for data_frame in data_li:
            data_frame = data_frame.values.tolist()
            print(data_frame)
            client2.execute('INSERT INTO f_weibo_blog_comment_an VALUES', data_frame, types_check=True)
        data_li = []

    bb = '生产了%s条数据!   生产时间%s' % (count, producte)
    bobao(content=bb)
    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if len(data_li)==0:
        b = '程序执行完成!   结束时间%s'%(end_time)
        bobao(content=b)


