"""

Программа парсит с сайта 1С (https://1c.ru/rus/partners/franch-citylist.jsp)
список партнеров и сохраняет в файлы .CSV и .TXT(столбцы разделе TAB) в формате
Город, Название партнера, URL, телефон

Использованы библиотеки:
requests, BeautifulSoup, lxml, panda

Последние изменение: 23.05.2022

"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd


def get_1c_parners_page(p):
    url_1c = 'https://1c.ru/rus/partners/franch-citylist.jsp?pageNumber_inp=' \
        + str(p)
    r = requests.get(url_1c)
    if r.status_code != 200:
        print('Не могу получить URL' + url_1c)
        exit()
    return bs(r.text, "lxml")


soup = get_1c_parners_page(1)

# парсим на 1ой странице номер последней страницы
max_page = int(soup.find('a', text=">>")['onclick'][-4:-1])

data = []
for page in range(1, max_page+1):
    print('Страница ' + str(page) + ' из ' + str(max_page))
    data.append([page])
    if page > 1:
        # получаем все страницы больше 1ой, тк 1ая уже получена
        soup = get_1c_parners_page(page)
    for tr in soup.find_all('tr'):
        i = 0
        [city, firm, url, phone] = ['', '', '', '']
        for td in tr.find_all('td'):
            s = td.text.strip()
            if len(s) > 0:
                if i == 0:
                    city = s
                elif i == 1:
                    # для некоторых фирм не указан url
                    u = td.find(lambda href: 'http' in str(href))
                    if u:
                        url = u.string
                    firm = s.split('\n')[0].replace('\x00', '')
                else:
                    phone = s
                i += 1
        data.append([city, firm, url, phone])
    print('Всего найдено ' + str(len(data)) + ' партнеров')

# сохраняем все в res.txt
fd = open('res.txt', 'w', encoding='utf8')
for s in data:
    r1 = ''
    for d in s:
        r1 = r1 + str(d) + '\t'
    fd.write(r1.strip() + '\n')
fd.close

# сохраняем все в res.csv
header = ['city', 'firm', 'url', 'phone']
df = pd.DataFrame(data, columns=header)
df.to_csv('res.csv', sep=';', encoding='cp1251')
