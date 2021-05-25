import re
import urllib.request, urllib.error

if __name__ == '__main__':
    baseurl = 'https://www.biorxiv.org'
    findTargetLink = re.compile(
        r'<span class="highwire-cite-title" >[\n\r ]+<a href="(.*?)".*?<span class="highwire-cite-title">(.*?)</span>'
    )


    for i in range(2):
        headers = {'User-Agent':'Mozilla/5.0xxxx'}
        url = urllib.request.Request(baseurl + '/content/early/recent?page=' +
                                    str(i), headers=headers)
        html = urllib.request.urlopen(url)
        html_text = bytes.decode(html.read())
        # print(html_text)

        target_urls = findTargetLink.findall(html_text)
        # print(target_urls)

        for j in range(len(target_urls)):
            try:
                # print(baseurl + target_urls[j][0] + '.full.pdf')
                urllib.request.urlretrieve(
                    baseurl + target_urls[j][0] + '.full.pdf',
                    './test_article/' + target_urls[j][1] + '.pdf')
                print('The ' + str(j + i * 10) +
                      ' th article has been downloaded.')
            except Exception:
                print('Failed!')
                continue