import pdfplumber
from PyPDF2 import PdfFileReader
import os
import re
import numpy as np
from decimal import Decimal

class PDF_Content:

    def __init__(self,path):
        self.path=path
        self.title = ''
        self.txt = ''
        self.abstract = ''
        self.introduction = ''
        self.__extract_text = ''

    def getContent(self):
        self.__getTitleByPyPDF2()#使用PyPDF2获得标题

        self.__extractText()#划分出正文区域，提取为txt
        # with open(save_path + 'total/' + 'text' + '.txt','w+',encoding='utf-8') as f_abs:
        #     f_abs.write(self.__extract_text)

        self.__getAbstractAndIntroduction()#从txt提取Abstract、Introduction

    def __getTitleByPdfplumber(self,page):
        words = page.extract_words(x_tolerance=2, y_tolerance=2,keep_blank_chars=True,use_text_flow=True,extra_attrs=["size"])
        size = []
        for word in words:
            size.append(word['size'])
            # print(word)
        #按字号大小选择标题
        size=np.sort(list(set(size)))
        for i in range(len(size)):
            max_size=size[-i-1]
            for word in words:
                if word['size'] == max_size:
                    self.title += word['text']
            if len(self.title)>5:
                break#去掉过短的串
            else:
                self.title = ''

    def __getTitleByPyPDF2(self):
        with open(self.path,'rb') as f:
            pdf=PdfFileReader(f)
            info=pdf.getDocumentInfo()
            #number_of_pages=pdf.getNumPages()
            #print(info.title)
            self.title = info.title

    def __extractText(self):
        def extract_text_within_bbox(page,box):
            return page.within_bbox(box).extract_text(x_tolerance=2, y_tolerance=2)

        def get_main_body_row_height_and_font_size(pdf):
            delta_y0=[]
            last_y0=Decimal("0")
            font_size=[]
            #统计文章所有相邻单词纵坐标差
            for i in range(len(pdf.pages)):
                words = pdf.pages[i].extract_words(x_tolerance=2, y_tolerance=2,keep_blank_chars=True,use_text_flow=True)
                for word in words:
                    font_size.append(word["bottom"]-word["top"])
                    delta=word['top']-last_y0
                    last_y0 = word['top']
                    if delta<0:
                        delta=0
                    delta_y0.append(delta)
            #字号众数
            font_size_counts=np.bincount(font_size)#此步会将浮点数转换成整数
            font_size_counts[0]=0
            font_size_argmax = np.argmax(font_size_counts)
            #舍弃0元素后的众数是正文行距
            delta_y0_counts = np.bincount(delta_y0)#此步会将浮点数转换成整数
            delta_y0_counts[0]=0
            #print(delta_y0_counts)
            delta_y0_argmax = np.argmax(delta_y0_counts)
            return np.clip(delta_y0_argmax,1.2*font_size_argmax,3*font_size_argmax), font_size_argmax

        def division_row(words, row_height):
            y0 = []
            last_y0 = Decimal("0")
            row_pos=[]
            #统计本页所有相邻单词纵坐标差
            for word in words:
                y0.append(word['top'])
            y0=np.sort(y0)
            for y in y0:
                if y<0:
                    y=0
                delta = y-last_y0
                last_y0 = y
                #较大行距认为是段落的区分
                if delta > 1.5*row_height:
                    row_pos.append(y)
                    #print("分段位置：", y, "行距差：", delta)
            return row_pos

        def division_column(page, width,bbox_top, bbox_bottom,main_font_size):
            words = page.within_bbox([0, bbox_top, width, bbox_bottom]).extract_words(
                x_tolerance=2, y_tolerance=2, keep_blank_chars=True, use_text_flow=True)
            #统计单词开头的x位置
            x0 = []
            font_size=[]
            for word in words:
                # print(word)
                if word['x0'] < 0:
                    word['x0'] = 0
                x0.append(word['x0'])
                font_size.append(word["bottom"]-word["top"])
            if len(x0)==0:
                return
            #字号众数
            font_size_counts=np.bincount(font_size)#此步会将浮点数转换成整数
            font_size_counts[0]=0
            font_size_argmax = np.argmax(font_size_counts)
            #字号过小
            if font_size_argmax < Decimal('0.95')*main_font_size:
                return
            #寻找 最多和次多 单词开头 的x位置
            x0_counts = np.bincount(x0)  # 此步会将浮点数转换成整数
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

            if x0_counts[x0_second] > 10:
                #次多的行数大于10 认为是分栏结构
                # 去掉过小的分栏
                if x0_second - x0_first > width*Decimal('0.2'):
                    temp = extract_text_within_bbox(page,[x0_first-1, bbox_top, x0_second+1, bbox_bottom])
                    if temp is not None:
                        self.__extract_text += temp+'\n'
                        #print(temp+'\n')
                # 去掉过小的分栏
                if width - x0_second > width*Decimal('0.2'):
                    temp = extract_text_within_bbox(page,[x0_second-1, bbox_top, width, bbox_bottom])
                    if temp is not None:
                        self.__extract_text += temp+'\n'
                        #print(temp+'\n')
            else:
                #否则认为是单栏结构
                temp = extract_text_within_bbox(page,[x0_first-1, bbox_top, width, bbox_bottom])
                if temp is not None:
                    self.__extract_text += temp+'\n'
                    #print(temp+'\n')

        with pdfplumber.open(self.path) as pdf:
            #print("宽：",pdf.pages[0].width,"高：",pdf.pages[0].height)
            row_height, main_font_size = get_main_body_row_height_and_font_size(pdf)
            # print("正文行距：",row_height,"正文字号：",main_font_size)

            for i in range(len(pdf.pages)):
                #print("第",i,"页")
                words = pdf.pages[i].extract_words(
                    x_tolerance=2, y_tolerance=2, keep_blank_chars=True, use_text_flow=True)
                row_pos = np.asarray(division_row(words, row_height))
                #去除固定的页眉页脚
                header = Decimal('0.08') * pdf.pages[i].height
                footer = (Decimal('1') - Decimal('0.08')) * pdf.pages[i].height
                row_pos=np.append(row_pos,[header,footer])
                row_pos=row_pos[np.where((row_pos >= header) & (row_pos <= footer))]
                row_pos = np.sort(row_pos)
                #分栏并提取txt
                for j in range(1,len(row_pos)):
                    row_top=row_pos[j-1]
                    row_buttom=row_pos[j]
                    division_column(pdf.pages[i], pdf.pages[i].width, row_top, row_buttom,main_font_size)

            #print(self.__extract_text)

    def __getAbstractAndIntroduction(self):
        # deleteNumbers1 = re.compile(r'[0-9]+(.*)')
        # deleteNumbers2 = re.compile(r'(.*)[0-9]+')
        getAbstract = re.compile(r'[^\f\n\r]{0,8}Abstract', re.I)
        getIntroduction = re.compile(r'[^\f\n\r]{0,8}Introduction', re.I)
        getEndIndex = re.compile(r'[0-9 \.]*(.*)')
        getEnd = re.compile(r'[A-Za-z]+')

        abs_flag = 0
        intro_flag = 0
        lines = self.__extract_text.split('\n')
        for line in lines:

            matchAbs = getAbstract.match(line)
            matchIntro = getIntroduction.match(line)

            if matchAbs is not None and abs_flag == 0:
                abs_flag = 1
                self.abstract += line+'\n'
                self.txt += line+'\n'
                continue

            if abs_flag==1:
                line=getEndIndex.match(line).group(1)
                matchEnd = getEnd.findall(line)
                if len(matchEnd) <= 3 and len(
                        matchEnd) > 0 and '.' not in line:
                    abs_flag = 2
                else:
                    self.abstract += line+' '

            if matchIntro is not None and intro_flag == 0:
                intro_flag = 1
                self.introduction += line+'\n'
                self.txt += line+' '
                continue

            if intro_flag==1:
                line=getEndIndex.match(line).group(1)
                matchEnd = getEnd.findall(line)
                if len(matchEnd) <= 3 and len(
                        matchEnd) > 0 and '.' not in line:
                    intro_flag = 2
                else:
                    self.introduction += line+' '
            self.txt += line+' '


if __name__ == '__main__':
    pdf_path = './get_data/articles/'
    save_path = './get_data/pdf_contents/'

    files = os.listdir(pdf_path)
    for file in files:
        pdf_content=PDF_Content(pdf_path+file)
        pdf_content.getContent()
        with open(save_path + file + '.txt','w+',encoding='utf-8') as f_abs:
            f_abs.write(pdf_content.title+'\n\n')
            f_abs.write(pdf_content.abstract+'\n\n')
            f_abs.write(pdf_content.introduction+'\n\n')
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