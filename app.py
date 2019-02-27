from bs4 import BeautifulSoup
from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import requests ,time, datetime
from datetime import datetime ,timedelta
from apscheduler.schedulers.blocking import BlockingScheduler


###secret data
line_bot_api = LineBotApi('channel token')
handler = WebhookHandler('secret')
your_id = 'your id'

#data can be modified
content = "iphone"
url = 'https://www.ptt.cc/bbs/macshop/index.html'

###scheduler
sched = BlockingScheduler()
#time unit
onehour = timedelta(hours=1)
oneday = timedelta(days=1)

def getsoup(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text , 'html.parser')
    return soup

def next_page(url):
    soup = getsoup(url)
    btns = soup.find_all("a", class_="btn wide")
    for btn in btns:
        btn_name = btn.text
        if '‹ 上頁' in btn_name:
            btn_url = 'https://www.ptt.cc' + btn.get('href')
            return btn_url

#爬蟲function
def find_key(url, keyword, curtime):
    #初始
    dict_ptt = {}
    count = 0
    top = 0
    #update時間
    curdate = ' %d/%d' % (curtime.month , curtime.day)
    yesterdate = ' %d/%d' % ((curtime - oneday).month , (curtime - oneday).day)
    #爬最新頁
    soup = getsoup(url)
    result = soup.find_all("div", class_="r-ent")
    for article in result:
        a_article = article.select_one("a")
        title_url = 'https://www.ptt.cc' + a_article.get('href')
        title_name = article.find("div", class_="title").text
        title_date = article.find("div" , class_ = "date").text
        #日期判斷(今天加昨天的日期標籤都當作有效的，會抓時間標籤做一小時內的判斷)
        if title_date == curdate or title_date == yesterdate:
            soup2 = getsoup(title_url)
            metaline = soup2.find_all("div" , class_ = "article-metaline")
            for meta in metaline:
                metatext = meta.find("span", class_ = "article-meta-tag").text
                #進下一層抓時間
                if '時間' in metatext:
                    #title_time_text's form : "Fri Feb 22 16:37:53 2019"
                    title_time_text = meta.find("span" , class_ = "article-meta-value").text
                    #title_time's form : "2019-02-22 16:37:53"
                    title_time = datetime.strptime(title_time_text , '%a %b %d %H:%M:%S %Y')
                    #判斷時間
                    if title_time + onehour > curtime:
                        #count為非置頂且一小時內的項目
                        count += 1
                        # 判斷關鍵字
                        if keyword.upper() in title_name.upper() and '販售' in title_name:
                            dict_ptt.update({title_name : title_url})
        #置頂文章判斷
        else:
            top += 1
    #置頂＋需要爬第二頁
    if len(result) <= count + top and top > 0:
        dict2 = find_key(next_page(url) , keyword ,curtime)
        dict_ptt.update(dict2)
    return dict_ptt

def push_messager(data , user_id):
    line_bot_api.push_message(user_id, TextSendMessage(text=data))
    return True

def make_token(content, datasize, answer):
    dataform = '一小時內%s的貼文數:' % content + '%d' % datasize
    goodtoken = "{}\n{}".format(dataform, answer)
    return goodtoken

def dic_to_list(dict):
    list = ""
    for i in dict.items():
        list += i[0]
        list += i[1]
    return list

@sched.scheduled_job('cron', hour='0-23' , minute=0)
def myjob():
    curtime = datetime.fromtimestamp(time.time()) + timedelta(hours=8)
    reply_dict = find_key(url, content, curtime)
    answer = dic_to_list(reply_dict)
    mytoken = make_token(content, len(reply_dict), answer)
    push_messager(mytoken , daisy_id)
    push_messager(mytoken, your_id)

sched.start()

