from ast import keyword
import requests
import urllib
import time
import random
import csv

keyword_list = ['독서', '영화', '음악', '운동', '건강', 'IT', 
                '여행', '요리', '사회', '직장생활', '철학', '예술',
                '사랑', '역사', '에세이', '재테크', '창업', '글쓰기',
                '반려동물', '심리']

# keyword = input('키워드를 입력해주세요:')

for keyword in keyword_list:

    print('keyword:',keyword , ' url 스크래핑을 시작합니다.')

    api_root = 'https://api.brunch.co.kr/v1/top/keyword/'
    encoded_keyword = urllib.parse.quote(keyword)
    time_stamp = int(time.time()) * 1000

    post_list= []

    start = time.time()

    for i in range(2500):
        url = api_root + encoded_keyword + '?publishTime=' + str(time_stamp) + '&pickContentId='
        post_20 = requests.get(url)
        json_raw = post_20.json()
        json_post_list = json_raw['data']['articleList']
        for post in json_post_list:
            user_id = post['article']['profileId']
            post_num = post['article']['no']
            url = 'https://brunch.co.kr/' + '@' + str(user_id) + '/' + str(post_num)
            post_list.append(url)
            # print('post url:', url)
        if len(json_post_list) != 20:
            break;    
        time_stamp = str(json_post_list[-1]['timestamp'])
        time.sleep(random.uniform(0.2, 0.7))

    end = time.time() - start
    m = end // 60
    s = end % 60

    print('keyword:',keyword, '총 ', len(post_list), '개의 글을 스크랩했습니다.')
    print(m,'분 ', s,'초 소요됨.')

    with open(keyword + "_url_10000.csv", 'w', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerow(post_list)