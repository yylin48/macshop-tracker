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


###scheduler
sched = BlockingScheduler()
#time
onehour = timedelta(hours = 1)
oneday = timedelta(days = 1)
#config
content = "iphone"
url = 'https://www.ptt.cc/bbs/macshop/index.html'



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
    #config
    dict_ptt = {}
    count = 0
    top = 0
    curdate = ' %d/%d' % (curtime.month , curtime.day)
    yesterdate = ' %d/%d' % ((curtime - oneday).month , (curtime - oneday).day)
    soup = getsoup(url)
    result = soup.find_all("div", class_="r-ent")

    for article in result:
        a_article = article.select_one("a")
        title_url = 'https://www.ptt.cc' + a_article.get('href')
        title_name = article.find("div", class_="title").text
        title_date = article.find("div" , class_ = "date").text
        #日期判斷(今天加昨天的日期標籤都當作有效的，反正之後會抓時間標籤做一小時內的判斷)
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
                        count += 1
                        # 判斷關鍵字
                        if keyword.upper() in title_name.upper():
                            dict_ptt.update({title_name : title_url})
        #置頂文章判斷
        else:
            top += 1

    #需要爬第二頁
    if len(result) <= count + top and top > 0:
        dict2 = find_key(next_page(url) , keyword ,curtime)

        dict_ptt.update(dict2)

    return dict_ptt


def push_messager(data):
    line_bot_api.push_message(your_id, TextSendMessage(text=data))
    return True

@sched.scheduled_job('cron', hour='0-23' , minute=0)
def myjob():
    answer = ""
    curtime = datetime.fromtimestamp(time.time()) +timedelta(hours=8)
    reply_dict = find_key(url, content, curtime)
    for i in reply_dict.items():
        answer += i[0]
        answer += i[1]
    datasize = '%d' %len(reply_dict)
    dataform = '一小時內%s的貼文數:' % content + datasize
    mytoken = "{}\n{}".format(dataform, answer)
    push_messager(mytoken)

sched.start()

