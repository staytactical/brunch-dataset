import csv

keyword = input('키워드를 입력해주세요:')

url_list = []

with open(keyword + '_url_10000.csv', mode='r') as fp:
    reader = csv.reader(fp)
    for line in reader:
        url_list = line
        # print(url_list)

print(keyword, '로 수집한 url은 총 ', len(url_list),'개 입니다.')