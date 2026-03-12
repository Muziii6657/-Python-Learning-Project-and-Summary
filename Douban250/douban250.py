from bs4 import BeautifulSoup
import requests
import csv
import time
# 服务器地址
url = "https://movie.douban.com/top250"
# 伪装成浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}
all_movie = []

# 遍历10页（每页25部，共250部）
for start in range(0, 250, 25):
    url = f"https://movie.douban.com/top250?start={start}"
    print(f"正在爬取: {url}")

# 发送请求
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    html_code = resp.text #提取，作为 BeautifulSoup 的输入
    # print(resp.text)
    # 得到 BeautifulSoup 对象。万里长征的第一步。
    bs = BeautifulSoup(html_code, "html.parser")
    # div_tag = bs.find("div",class_='info')
    div_tags = bs.find_all("div",class_='info')
    # print(div_tags)
    # print(type(div_tags[0]))
    for div_tag in div_tags:
        div_tag_name = div_tag.find("span",class_='title').contents
        # print(div_tag_name)
        div_tag_link = div_tag.find("a").attrs['href']
        div_tag_judge = div_tag.find("span", attrs={"class":"rating_num" ,"property":"v:average"}).contents
        movie_name = div_tag_name[0]
        movie_link = div_tag_link
        movie_judge = div_tag_judge[0]
        all_movie.append([movie_name,movie_link,movie_judge])

    # 礼貌等待1秒，降低被反爬风险
    time.sleep(1)

with open("films.csv",'w',newline='') as f:
    csv_movieT250 = csv.writer(f)
    csv_movieT250.writerow(["电影名称","电影链接","电影评分"])
    csv_movieT250.writerows(all_movie)

print(f"成功保存 {len(all_movie)} 部电影到 films.csv")