import re
import urllib.request, urllib.error
import threading
import time

def getData(index):
    for word in ch_words:
        for i in range(index, index+10):
            html = urllib.request.urlopen(
                baseurl + '/search/?q=' + urllib.parse.quote(word) +
                '&f_journalif=2&to_journalif=15&sort=year&current_page=' +
                str(i))
            html_text = bytes.decode(html.read())

            # with open('html.txt', 'w+') as f:
            #     f.write(html_text)

            target_urls = findTargetLink.findall(html_text)
            # print(target_urls)

            for url in target_urls:
                try:
                    html = urllib.request.urlopen(baseurl + url)
                    html_text = bytes.decode(html.read())

                    lock.acquire()
                    chTitle.append(findChTitle.search(html_text))
                    chAbstract.append(findChAbstract.search(html_text))
                    enTitle.append(findEnTitle.search(html_text))
                    enAbstract.append(findEnAbstract.search(html_text))
                    lock.release()

                    # print('Get!')

                except Exception:
                    print('The article at '+ str(baseurl + url) + ' is lost! \n')
                    continue

ch_words = [
    '研究', '技术', '系统', '结构', '功能', '治疗', '病毒', '疾病', '生物', '分子', '细胞', '蛋白质',
    '性状', '细菌', '分泌', '遗传'
]

baseurl = 'http://www.chinapubmed.net'
findTargetLink = re.compile(
    r'<div class="paper-list-title" style="font-size: 14px">[\n\r ]+<a href="(.*?)">'
)
findChTitle = re.compile(
    r'<div class="cntitle" style="margin-top: 30px;text-align: center">[\n\r ]+<span>(.*?)\*\*</span>'
)
findChAbstract = re.compile(
    r'<div class="cnabstract" style="margin-top: 10px">[\n\r ]+<span>(.*?)\*\*</span>'
)
findEnTitle = re.compile(
    r'<div class="entitle" style="margin-top: 30px;text-align: center">[\n\r ]+<span>(.*?)</span>'
)
findEnAbstract = re.compile(
    r'<div class="enabstract" style="margin-top: 10px">[\n\r ]+<span>(.*?)</span>'
)

chTitle = []
chAbstract = []
enTitle = []
enAbstract = []

lock = threading.Lock()

if __name__ == '__main__':

    threads = []
    for i in range(2):
        threads.append(threading.Thread(target=getData, args=(i*10,)))
        threads[i].start()

    for thread in threads:
        thread.join()
    time.sleep(0.1)

    with open('./data/abstract.zh', 'w+') as f:
        for line in chAbstract:
            if line is not None:
                f.writelines(line.group(1)+'\n')
            else:
                f.writelines('\n')

    with open('./data/abstract.en', 'w+') as f:
        for line in enAbstract:
            if line is not None:
                f.writelines(line.group(1)+'\n')
            else:
                f.writelines('\n')

    with open('./data/title.zh', 'w+') as f:
        for line in chTitle:
            if line is not None:
                f.writelines(line.group(1)+'\n')
            else:
                f.writelines('\n')

    with open('./data/title.en', 'w+') as f:
        for line in enTitle:
            if line is not None:
                f.writelines(line.group(1)+'\n')
            else:
                f.writelines('\n')
