import re
import os.path
from itertools import count
from threading import Thread

import requests
import bs4
from bs4.element import Tag

def fetch_school(id, result, i):
    url = 'http://college.gaokao.com/school/tinfo/{}/intro/'.format(id)
    while True:
        try:
            res = requests.get(url)
            break
        except requests.exceptions.ConnectTimeout:
            print('Connect timeout')
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    title = soup.find('div', class_='bg_sez').h2.string
    print(title)
    result[i] = (
        title, 
        re.sub(
            '(\s)\s*', 
            r'\1', 
            re.sub(
                '。|？|！|……',
                '\n',
                ''.join(map(Tag.get_text, soup.find('div', class_='jj').find_all('p')))
            )
        )
    )

def fetch_page(ids):
    threads = []
    result = [None] * len(ids)
    for (i, id) in enumerate(ids):
        thread = Thread(
            target=fetch_school,
            args=(id, result, i)
        )
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    for name, content in result:
        open(os.path.join('result', name + '.txt'), 'w', encoding='utf-8').write(content)

def main():
    url = 'http://college.gaokao.com/schlist/s1/'
    for page in count(1):
        print('第', page, '页')
        res = requests.get(url)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        fetch_page(
            [
                int(re.match(r'http://college.gaokao.com/school/(\d+)/', a['href']).group(1))
                for link in soup.find('div', class_='scores_List').find_all('dt')
                if (a := link.a) is not None
            ]
        )
        next = soup.find('a', string='下一页 >>')
        if next is None:
            print('done')
            break
        url = next['href']

if __name__ == '__main__':
    main()