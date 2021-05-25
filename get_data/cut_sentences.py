from nltk.tokenize import sent_tokenize

import re
def zh_cut_sent(para):
    para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return para.split("\n")

def cut_sentence():
    successCount = 0
    failCount = 0

    en = open('../data/abstract.en', 'r+')
    zh = open('../data/abstract.zh', 'r+')

    enList = []
    zhList = []
    enSentenceList = []
    zhSentenceList = []
    enNoRepeatList = []
    zhNoRepeatList = []

    for line in en.readlines():
        enList.append(line)

    for line in zh.readlines():
        zhList.append(line)

    for i in range(len(enList)):
        if not enList[i] in enNoRepeatList:
            enNoRepeatList.append(enList[i])
        if not zhList[i] in zhNoRepeatList:
            zhNoRepeatList.append(zhList[i])

    for i in range(len(enNoRepeatList)):
        enTmp = sent_tokenize(enNoRepeatList[i])
        zhTmp = zh_cut_sent(zhNoRepeatList[i])
        if len(enTmp) != len(zhTmp):
            failCount += 1
        else:
            enSentenceList += enTmp
            zhSentenceList += zhTmp
            successCount += 1
    print(successCount, failCount)

    en.close()
    zh.close()

    with open('../data/abstract_cut.en', 'w+') as f:
        for sen in enSentenceList:
            f.write(sen + '\n')
    with open('../data/abstract_cut.zh', 'w+') as f:
        for sen in zhSentenceList:
            f.write(sen + '\n')

# cut_sentence()

def cut_sent():
    en = open('../data/abstract.en', 'r+')
    zh = open('../data/abstract.zh', 'r+')

    enList = []
    zhList = []
    enSentenceList = []
    zhSentenceList = []
    enNoRepeatList = []
    zhNoRepeatList = []

    for line in en.readlines():
        enList.append(line)

    for line in zh.readlines():
        zhList.append(line)

    for i in range(len(enList)):
        if not enList[i] in enNoRepeatList:
            enNoRepeatList.append(enList[i])
        if not zhList[i] in zhNoRepeatList:
            zhNoRepeatList.append(zhList[i])

    for i in range(len(enNoRepeatList)):
        enSentenceList += sent_tokenize(enNoRepeatList[i])
        zhSentenceList += zh_cut_sent(zhNoRepeatList[i])

    en.close()
    zh.close()

    with open('../data/abstract_cut_no_align.en', 'w+') as f:
        for sen in enSentenceList:
            f.write(sen + '\n')
    with open('../data/abstract_cut_no_align.zh', 'w+') as f:
        for sen in zhSentenceList:
            f.write(sen + '\n')
            
if __name__=='__main__':
    cut_sent()

# def ch_cut_sent(infile, outfile):
#     cutLineFlag = ["？", "！", "。","…"] #本文使用的终结符，可以修改
#     sentenceList = []
#     with open(infile, "r+", encoding="UTF-8") as f:
#         oneSentence = ""
#         for line in f:
#             words = line.strip()
#             if len(oneSentence)!=0:
#                 sentenceList.append(oneSentence.strip() + "\n")
#                 oneSentence=""
#             # oneSentence = ""
#             for word in words:
#                 if word not in cutLineFlag:
#                     oneSentence = oneSentence + word
#                 else:
#                     oneSentence = oneSentence + word
#                     if oneSentence.__len__() > 4:
#                         sentenceList.append(oneSentence.strip() + "\n")
#                     oneSentence = ""
#     with open(outfile, "w+", encoding="UTF-8") as resultFile:
#         # print(sentenceList.__len__())
#         resultFile.writelines(sentenceList)


# en_cut_sent('../data/abstract.en', '../data/abstract_cut.en')
# # ch_cut_sent('../data/abstract.zh', '../data/abstract_cut.zh')