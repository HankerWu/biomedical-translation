import pdfplumber
from PyPDF2 import PdfFileReader
import os
import re
import numpy as np
from decimal import *


class PDF_Content:
    def __init__(self, path):
        self.path = path
        self.title = ''
        self.txt = ''
        self.abstract = ''
        self.introduction = ''
        self.__extract_text = ''

    def getContent(self):
        self.__getTitleByPyPDF2()  #使用PyPDF2获得标题

        self.__extractText()  #划分出正文区域，提取为txt
        # with open(save_path + 'total/' + 'text' + '.txt','w+',encoding='utf-8') as f_abs:
        #     f_abs.write(self.__extract_text)

        self.__getAbstractAndIntroduction()  #从txt提取Abstract、Introduction

    def __getTitleByPdfplumber(self, page):
        words = page.extract_words(x_tolerance=2,
                                   y_tolerance=2,
                                   keep_blank_chars=True,
                                   use_text_flow=True,
                                   extra_attrs=["size"])
        size = []
        for word in words:
            size.append(word['size'])
            # print(word)
        #按字号大小选择标题
        size = np.sort(list(set(size)))
        for i in range(len(size)):
            max_size = size[-i - 1]
            for word in words:
                if word['size'] == max_size:
                    self.title += word['text']
            if len(self.title) > 5:
                break  #去掉过短的串
            else:
                self.title = ''

    def __getTitleByPyPDF2(self):
        with open(self.path, 'rb') as f:
            pdf = PdfFileReader(f)
            info = pdf.getDocumentInfo()
            #number_of_pages=pdf.getNumPages()
            #print(info.title)
            self.title = info.title

    def __extractText(self):
        with pdfplumber.open(self.path) as pdf:
            for i in range(len(pdf.pages)):
                words = pdf.pages[i].extract_words(x_tolerance=2,
                                                   y_tolerance=2,
                                                   keep_blank_chars=True,
                                                   use_text_flow=True)

                #统计单词开头的x位置
                x0 = []
                for word in words:
                    # print(word)
                    if word['x0'] < 0:
                        word['x0'] = 0
                    x0.append(word['x0'])

                #寻找 最多和次多 单词开头 的x位置
                x0_counts = np.bincount(x0)
                # print(x0_counts)
                x0_argsort = np.argsort(x0_counts)
                x0_first = x0_argsort[-1]
                x0_second = x0_argsort[-2]
                # print(x0_argsort)
                if x0_first > x0_second:
                    x0_first, x0_second = x0_second, x0_first
                if x0_first < 1:
                    x0_first = 1
                if x0_second < 1:
                    x0_second = 1

                #删去固定的页眉页脚
                bbox_top = Decimal('0.08') * pdf.pages[i].height
                bbox_bottom = (Decimal('1') -
                               Decimal('0.08')) * pdf.pages[i].height

                if x0_counts[x0_second] > 10:
                    #次多的行数大于10 认为是分栏结构
                    if x0_second - x0_first > pdf.pages[i].width * Decimal(
                            '0.2'):  #去掉过小的分栏
                        temp = pdf.pages[i].within_bbox([
                            x0_first - 1, bbox_top, x0_second + 1, bbox_bottom
                        ]).extract_text(x_tolerance=2, y_tolerance=2)
                        if temp is not None:
                            self.__extract_text += temp + '\n'
                    if pdf.pages[i].width - x0_second > pdf.pages[
                            i].width * Decimal('0.2'):  #去掉过小的分栏
                        temp = pdf.pages[i].within_bbox([
                            x0_second - 1, bbox_top, pdf.pages[i].width,
                            bbox_bottom
                        ]).extract_text(x_tolerance=2, y_tolerance=2)
                        if temp is not None:
                            self.__extract_text += temp + '\n'
                else:
                    #否则认为是单栏结构
                    temp = pdf.pages[i].within_bbox([
                        x0_first - 1, bbox_top, pdf.pages[i].width, bbox_bottom
                    ]).extract_text(x_tolerance=2, y_tolerance=2)
                    if temp is not None:
                        self.__extract_text += temp + '\n'
            # print(self.__extract_text)

    def __getAbstractAndIntroduction(self):
        deleteNumbers1 = re.compile(r'[0-9]+(.*)')
        deleteNumbers2 = re.compile(r'(.*)[0-9]+')
        getAbstract = re.compile(r'[^\f\n\r]{0,8}Abstract', re.I)
        getIntroduction = re.compile(r'[^\f\n\r]{0,8}Introduction', re.I)
        getEndIndex = re.compile(r'[0-9 \.]*(.*)')
        getEnd = re.compile(r'[A-Za-z]+')

        abs_flag = False
        intro_flag = False
        lines = self.__extract_text.split('\n')
        j = 0
        for line in lines:

            # matchDel1 = deleteNumbers1.match(line)
            # matchDel2 = deleteNumbers2.match(line)

            # if matchDel1 is not None:
            #     line = matchDel1.group(1) + '\n'
            # elif matchDel2 is not None:
            #     if line == matchDel2.group():
            #         line = matchDel2.group(1) + '\n'
            #     else:
            #         line += '\n'
            # else:
            #     line += '\n'

            # matchDel1 = deleteNumbers1.match(line)
            # if matchDel1 is not None and line == matchDel1.group():
            #     continue
            matchAbs = getAbstract.match(line)
            matchIntro = getIntroduction.match(line)

            if matchAbs is not None:
                abs_flag = True
                self.abstract += line + '\n'
                self.txt += line
                continue

            if abs_flag:
                line = getEndIndex.match(line).group(1)
                matchEnd = getEnd.findall(line)
                if len(matchEnd) <= 3 and len(
                        matchEnd) > 0 and '.' not in line:
                    abs_flag = False
                else:
                    self.abstract += line

            if matchIntro is not None:
                intro_flag = True
                self.introduction += line + '\n'
                self.txt += line
                continue

            if intro_flag:
                line = getEndIndex.match(line).group(1)
                matchEnd = getEnd.findall(line)
                if len(matchEnd) <= 3 and len(
                        matchEnd) > 0 and '.' not in line:
                    intro_flag = False
                else:
                    self.introduction += line
            self.txt += line


if __name__ == '__main__':
    pdf_path = './test_article/'
    save_path = './test_txt/'

    files = os.listdir(pdf_path)
    for file in files:
        pdf_content = PDF_Content(pdf_path + file)
        pdf_content.getContent()
        with open(save_path + file + '.txt', 'w+',
                  encoding='utf-8') as f_abs:
            f_abs.write(pdf_content.title + '\n\n')
            f_abs.write(pdf_content.abstract + '\n\n')
            f_abs.write(pdf_content.introduction + '\n\n')
        # with open(save_path + 'abstract/' + file + '.txt',
        #           'w+',
        #           encoding='utf-8') as f_abs:
        #     f_abs.write(abstract)
        # with open(save_path + 'introduction/' + file + '.txt',
        #           'w+',
        #           encoding='utf-8') as f_intro:
        #     f_intro.write(introduction)

        print(pdf_content.title)
        # print(pdf_content.abstract)
        # print(pdf_content.introduction)