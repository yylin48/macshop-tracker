import time, requests, datetime ,logging, os
from datetime import datetime , timedelta
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from linebot import LineBotApi, WebhookHandler
from env import *
from linebot.models import TextSendMessage

#scheduler
sched = BlockingScheduler()

###channel token
line_bot_api = LineBotApi(channel_token)
###secret
handler = WebhookHandler(secret)

#time
onehour = timedelta(hours = 1)
oneday = timedelta(days = 1)
eighthour = timedelta(hours= 8)
macshop_url = 'https://www.ptt.cc/bbs/macshop/index.html'
keyword = "iphone"

class Logger:
    def __init__(self, path, filename):
        if not os.path.exists(path + '/log'):
            os.makedirs(path + '/log')
        logging.basicConfig(level=logging.INFO,
            format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt = '%m-%d %H:%M:%S',
            filename = path+'/log/'+filename)
    def info(self, string):
        print("[INFO] " + string)
        logging.info(string)
    def error(self, string):
        print("[ERROR] " + string)
        logging.error(string)


class crawler():
    def __init__(self):
        self.user_id = []
        self.list = ""
        self.count = 0
        self.logging = Logger(os.path.dirname(os.path.abspath(__file__)), datetime.now().strftime("macshop.%Y-%m.log"))

    def get_keyword(self, keyword):
        self.keyword = keyword

    def get_url(self, url):
        self.url = url

    def getsoup(self):
        res = requests.get(self.url)
        return BeautifulSoup(res.text, 'html.parser')

    def next_page(self):
        btns = self.getsoup().find_all("a", class_="btn wide")
        for btn in btns:
            btn_name = btn.text
            if '‹ 上頁' in btn_name:
                btn_url = 'https://www.ptt.cc' + btn.get('href')
                self.url = btn_url

    def add_user_id(self , new_user_id):
        self.user_id.append(new_user_id)

    def time_update(self):
        self.curtime = datetime.fromtimestamp(time.time()) + eighthour
        self.yestertime = self.curtime - oneday
        self.curdate = ' %d/' % self.curtime.month + self.curtime.strftime("%d")
        self.yesterdate = ' %d/' % self.yestertime.month + self.yestertime.strftime("%d")

    def find_key(self):
        dict_ptt = {}
        count = 0
        top = 0
        result = self.getsoup().find_all("div", class_="r-ent")
        for article in result:
            a_article = article.select_one("a")
            title_url = 'https://www.ptt.cc' + a_article.get('href')
            title_name = article.find("div", class_="title").text
            title_date = article.find("div", class_="date").text
            # 日期判斷(今天加昨天的日期標籤都當作有效的，反正之後會抓時間標籤做一小時內的判斷)
            if title_date == self.curdate or title_date == self.yesterdate:
                res2 = requests.get(title_url)
                soup2 = BeautifulSoup(res2.text, 'html.parser')
                metaline = soup2.find_all("div", class_="article-metaline")
                for meta in metaline:
                    metatext = meta.find("span", class_="article-meta-tag").text
                    # 進下一層抓時間
                    if '時間' in metatext:
                        # title_time_text's form : "Fri Feb 22 16:37:53 2019"
                        title_time_text = meta.find("span", class_="article-meta-value").text
                        # title_time's form : "2019-02-22 16:37:53"
                        title_time = datetime.strptime(title_time_text, '%a %b %d %H:%M:%S %Y')
                        # 判斷時間
                        if title_time + onehour > self.curtime:
                            count += 1
                            # 判斷關鍵字
                            if self.keyword.upper() in title_name.upper() and '販售' in title_name:
                                dict_ptt.update({title_name: title_url})
            # 置頂文章判斷
            else:
                top += 1
        if len(result) <= count + top and top > 0:
            self.next_page()
            self.find_key()
        for i in dict_ptt.items():
            self.list += i[0]
            self.list += i[1]
            self.count += 1

    def generate_token(self):
        dataform = '一小時內%s的貼文數:' % self.keyword + '%d' % self.count
        self.token = "{}{}".format(dataform, self.list)
        self.logging.info(self.token)

    def line_bot_push(self):
        for id in self.user_id:
            line_bot_api.push_message(id, TextSendMessage(text=self.token))
            self.logging.info("push success")

@sched.scheduled_job('cron', hour='0-23', minute=0)
def myjob():
    a = crawler()
    a.get_keyword(keyword)
    a.get_url(macshop_url)
    a.time_update()
    a.find_key()
    #you can add several user id
    a.add_user_id(your_id)
    a.generate_token()
    a.line_bot_push()

if __name__ == "__main__":
    sched.start()
