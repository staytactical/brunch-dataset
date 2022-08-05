import requests
import urllib
import time
import random
import csv

keyword = input('키워드를 입력해주세요:')

api_root = 'https://api.brunch.co.kr/v1/top/keyword/'
encoded_keyword = urllib.parse.quote(keyword)
time_stamp = int(time.time()) * 1000

post_list= []

for i in range(1):
    url = api_root + encoded_keyword + '?publishTime=' + str(time_stamp) + '&pickContentId='
    post_20 = requests.get(url)
    json_raw = post_20.json()
    json_post_list = json_raw['data']['articleList']
    for post in json_post_list:
        user_id = post['article']['profileId']
        post_num = post['article']['no']
        url = 'https://brunch.co.kr/' + '@' + str(user_id) + '/' + str(post_num)
        post_list.append(url)
        print('post url:', url)
    if len(json_post_list) != 20:
        break;    
    time_stamp = str(json_post_list[-1]['timestamp'])
    time.sleep(random.randint(1, 2))

print('총 ', len(post_list), '개의 글을 스크랩했습니다. 프로그램을 종료합니다.')

url_dict = {}
url_dict[keyword] = post_list


with open("keyword_url_10000.csv", 'a', newline='') as file:
  writer = csv.writer(file)
  for k, v in url_dict.items():
       writer.writerow([k, v])