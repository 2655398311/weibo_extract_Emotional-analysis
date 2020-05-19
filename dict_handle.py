# #词典整理
import pandas as pd
#
# #，否定词典
# no_dict = open('data/其他词典和分类/否定词典/否定.txt')
# text_no = no_dict.readlines()
# for i in text_no:
#     print(i)
#
# #情感词典及多分类
# multi_dict = open('abc1.txt',encoding='utf-8')
# mutli_res = open('multi.txt','w',encoding='utf-8')
# text_multi = multi_dict.readlines()
# for i in text_multi:
#     mutli_res.writelines(i.replace('\t',','))
#
# multi_dict = pd.read_csv('multi.csv',encoding='utf-8')
# # a = list(set(multi_dict['Class']))
# a = ['感动','祝愿', '喜欢', '佩服','道谢', '舒畅','赞成', '激动', '愿意', '高兴','留恋', '心静', '感激'
#  '喜爱', '无愧', '得意', '满意', '振奋', '称赞', '镇定', '倾心']
# b= ['委屈', '烦闷', '忧愁', '责骂', '心虚', '慌张', '仇恨', '厌烦', '惭愧',
#  '鄙视', '责怪', '失望', '哭泣',  '不满', '悲伤', '怨恨', '漠视'
#  '害怕', '着急',  '痛苦', '不安', '惆怅',  '愤怒']
# f = open('dict_res/贬义1.txt','w',encoding='utf-8')
# baoyi = []
# for i in b:
#     baoyi += (list(multi_dict[multi_dict['Class']==i]['Instance']))
# baoyi = list(set(baoyi))
# for i in baoyi:
#     f.writelines(i+'\n')
# # 情感词汇本体
# base_dict =
import pandas as pd
# a = pd.read_excel('dict_res/褒贬词及其近义词.xls')
# a[a['褒贬色彩']=='贬义'].to_csv('dict_res/贬义词.csv',index=False)
# f = open('dict_res/贬义.txt','w',encoding='utf-8')
# temp = open('dict_res/贬义词.txt',encoding='gbk').read().replace(',','\n').replace('/','\n').replace('\n\n','\n')
# f.write(temp)
# str_all = ''
# for i in range(8):
#     f = open('data/中间处理/n' + str(i + 1) + '.txt', encoding='utf-8')
#     str_all += f.read()+'\n'
#
# str_final = str_all.replace('\n\n','\n').replace('\n\n','\n').replace('\n\n','\n')\
#     .replace('\n\n','\n').replace('\n\n','\n').replace('\n\n','\n')\
#     .replace('\n\n','\n').replace('\n\n','\n').replace('\n\n','\n')
#
# str_final = list(set(str_final.split('\n')))
# print(len(str_final))
# str_final = '\n'.join(str_final)
# print(str_final)
# f1 = open('negtive_all.txt','w',encoding='utf-8')
# f1.write(str_final)

# 得正情感词16129，负情感词12397

# f1 = open('jizhi.txt','w',encoding='utf-8')
# f = open('dict_res/汉语情感词极值表.txt',encoding='utf-8')
# text = f.read().replace('\t',',')
# f1.write(text)

# import pandas as pd
# a = pd.read_csv('dict_res/jizhi.csv',encoding='utf-8')
# a['value'] = 5 - 10*(max(a['极值'])-a['极值'])/(max(a['极值'])-min(a['极值']))
# a1 = a[['词语','value']]
# print(min(a1['value']))
# print(max(a1['value']))
# a1.to_csv('dict_res/jizhi_first.csv',encoding = 'utf-8',index = False)
#
# b = pd.read_excel('dict_res/情感词汇本体.xlsx',encoding = 'utf-8')
# b1 = b[b['极性']==2]
# b2 = b[b['极性']!=2]
# b1['极性'] = -1
# c = b1.append(b2)
# c['极值'] = c['强度']*c['极性']*5/9
# d = c[['词语','极值']]
# print(min(d['极值']))
# print(max(d['极值']))

# print(c[c['极值']==9])
# print(b[b['极性']==3])
# d.to_csv('dict_res/jizhi_second.csv',encoding = 'utf-8',index = False)
# a = pd.read_csv('dict_res/jizhi_second.csv',encoding = 'utf-8')
# c = a.loc[a['word']=='不错',['value']].sum()
# if c.any():
#     print(c)
# a1 = list(a['word'])
# b = open('dict_res/程度级别.txt ',encoding = 'utf-8')
# b1 = b.read().split('\n')
# print(set(a1)&set(b1))
#
# print({1,2}=={2,2})
#
# from pyhanlp import HanLP
#
# a = HanLP.segment('我在 豪泰 旗舰店')
# print(a)
print([][0])