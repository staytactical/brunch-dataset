import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def download(url, user_agent='wswp', num_retries=2, proxies=None):
    print('Downloading', url)
    headers = {'User-Agent' : user_agent}
    try:
        resp = requests.get(url, headers=headers, proxies=proxies)
        html = resp.text
        if resp.status_code >= 400:
            print('Download error:', resp.text)
            html = None
            if num_retries and 500 <= resp.status_code < 600:
                return download(url, num_retries - 1)
    except requests.exceptions.RequestException as e:
        print('Download error:', e.reason)
        html = None
    return html

def decode_post_date(src):
    dict_month = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 
                  'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    if '분전' in src or '시간전' in src:
        date = datetime.today().strftime("%Y-%m-%d")
    else:
        m = dict_month[src[:3]]
        d = src[4:6]
        y = src[7:]
        date = y + '-' + m + '-' + d 
    return date

def no_spaces(str):
    text = str.replace(" ", '')
    text = text.replace('\n', '')
    return text

def no_comma(str):
    text = str.replace(',','')
    return text

url = input('스크랩하고자 하는 url을 입력해주세요: ')
html = download(url)
soup = BeautifulSoup(html, 'lxml')

title = soup.find('h1',attrs={'class':'cover_title'}).text

sub_title = soup.find('p', attrs={'class':'cover_sub_title'}).text

body_text = soup.find_all(['p','h4'], attrs={'class':'wrap_item item_type_text'})
text = ''
for s in body_text:
    text = text + ' ' + s.text.replace('\xa0',' ')

likes = soup.find('span', attrs={'class': 'f_l text_like_count text_default text_with_img_ico ico_likeit_like #like'}).text
likes = 0 if likes=='' else int(no_comma(likes))

num_comments = soup.find('span', attrs={'class':'f_l text_comment_count text_default text_with_img_ico'}).text
num_comments = 0 if num_comments=='' else int(no_comma(num_comments))

post_date = soup.find('span',attrs={'class':'f_l date'}).text

keyword_list = []
first_keyword = soup.find('ul', attrs={'class':'list_keyword'}).li
keyword_list.append(no_spaces(first_keyword.get_text()))
other_keywords = first_keyword.find_next_siblings('li')
for keyword in other_keywords:
    keyword_list.append(no_spaces(keyword.text))

author = soup.find('span', attrs={'class':'f_l text_author #author'}).a.text
author_page = soup.find('span', attrs={'class':'f_l text_author #author'}).a['href']
author_id = author_page.replace('https://brunch.co.kr/','')
try:
    author_belong = soup.find('span', attrs={'class':'author_belong'}).span.find_next_sibling('span').get_text()
except AttributeError as e:
    author_belong = "직업없음"
author_desc = soup.find('p', attrs={'class':'txt_desc'}).text
num_subscription = soup.find('span', attrs={'class':'num_subscription'}).text
num_subscription = 0 if num_subscription=='' else int(no_comma(num_subscription))

print('title:', title)
print('sub_title:', sub_title)
print('body_text:', text)
print('likes:',likes)
print('num_comments:', )
print('post_date:', decode_post_date(post_date))
print('kewords:', keyword_list)
print('author:', author)
print('author_id:', author_id)
print('author_belong:',author_belong)
print('author_desc:', author_desc)
print('num_subscription:', num_subscription)