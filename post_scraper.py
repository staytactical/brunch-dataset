import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time
import random
import string
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

def over_thousand(str):
    punct = string.punctuation
    if '만' in str:
        text = re.sub(r'[^\w\s]','',str)
        text = text.replace('만','')
        text = text + '000'
        return text
    text = str.replace(',','')
    return text

def scrap_single_post(url):
    html = download(url)
    if html is None:
        return None

    soup = BeautifulSoup(html, 'lxml')

    title = soup.find('h1',attrs={'class':'cover_title'}).text

    sub_title = soup.find('p', attrs={'class':'cover_sub_title'}).text

    body_text = soup.find_all(['p','h2','h3','h4','h5','h6'], attrs={'class':'wrap_item item_type_text'})
    text = ''
    for s in body_text:
        text = text + ' ' + s.text.replace('\xa0',' ')

    likes = soup.find('span', attrs={'class': 'f_l text_like_count text_default text_with_img_ico ico_likeit_like #like'}).text
    likes = 0 if likes=='' else int(over_thousand(likes))

    try:
        num_comments = soup.find('span', attrs={'class':'f_l text_comment_count text_default text_with_img_ico'}).text
        num_comments = 0 if num_comments=='' else int(over_thousand(num_comments))
    except AttributeError:
        num_comments = 0

    post_date = soup.find('span',attrs={'class':'f_l date'}).text
    post_date = decode_post_date(post_date)

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
        author_belong = ""
    try:    
        author_desc = soup.find('p', attrs={'class':'txt_desc'}).text
    except AttributeError:
        author_desc = ""

    num_subscription = soup.find('span', attrs={'class':'num_subscription'}).text
    num_subscription = 0 if num_subscription=='' else int(over_thousand(num_subscription))

    scrap_result = {'title':title, 'sub_title':sub_title, 'body_text':text, 'keyword':keyword_list, 'likes':likes, 
                    'num_comments':num_comments,'post_date':post_date, 'post_url':url, 'author':author, 'author_id':author_id,
                    'author_belong':author_belong, 'author_desc':author_desc, 'num_subscription':num_subscription }

    return scrap_result

def print_scrap_result(scrap_dict):
    print('title:', scrap_dict['title'])
    print('sub_title:', scrap_dict['sub_title'])
    print('body_text:',scrap_dict['body_text'])
    print('keywords:', scrap_dict['keyword'])
    print('likes:',scrap_dict['likes'])
    print('num_comments:', scrap_dict['num_comments'])
    print('post_date:', scrap_dict['post_date'])
    print('post_url:', scrap_dict['post_url'])
    print('author:', scrap_dict['author'])
    print('author_id:', scrap_dict['author_id'])
    print('author_belong:',scrap_dict['author_belong'])
    print('author_desc:', scrap_dict['author_desc'])
    print('num_subscription:', scrap_dict['num_subscription'])

def get_urls_from_csv(keyword):
    url_list = []

    with open('keyword_urls/' + keyword + '_url.csv', mode='r') as fp:
        reader = csv.reader(fp)
        for line in reader:
            url_list = line

    print(keyword, '로 수집한 url은 총 ', len(url_list),'개 입니다.')
    return url_list

def get_post_dict_list(url_list, keyword):
    dict_list = []

    for url in url_list:
        result = scrap_single_post(url)
        print_scrap_result(result)
        if result is None:
            continue
        result['keyword'] = keyword
        dict_list.append(result)
        time.sleep(random.uniform(0.001,0.05))
    return dict_list

def save_dict_list_to_csv(keyword, dict_list):
    labels = ['title','sub_title','body_text','keyword', 'likes',
                'num_comments','post_date','post_url','author',
                'author_id','author_belong','author_desc','num_subscription' ]
    try:
        with open( keyword + '_dataset.csv', 'w', -1, 'utf-8', newline='') as fp:
            writer = csv.DictWriter(fp, fieldnames = labels)
            writer.writeheader()
            for elem in dict_list:
                writer.writerow(elem)
    except IOError:
        print("I/O error")

keywords = ['IT', '건강', '독서', '사랑', '심리', '에세이', '여행',
            '역사', '영화', '예술', '운동', '음악', '직장생활',
            '창업', '철학']

for keyword in keywords:       
    start = time.time()
    url_list = get_urls_from_csv(keyword)
    dict_list = get_post_dict_list(url_list, keyword)
    save_dict_list_to_csv(keyword, dict_list)
    end = time.time() - start
    m = int(end // 60)
    s = int(end % 60)
    print(keyword + '_dataset.csv을 파일로 저장했습니다. 총',len(dict_list),'개의 글.', m,'분', s,'초 소요됨.')