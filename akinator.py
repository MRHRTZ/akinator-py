import re
import requests
import json


from datetime import datetime
from bs4 import BeautifulSoup

class Akinator:
    def __init__(self):
        self.region = {}
        self.main_url = 'https://en.akinator.com'
        self.base_url = ''
        self.jQuery = 'jQuery34108935586299516678_'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }

        self.urlWs = None 
        self.frontaddr = None
        self.channel = None 
        self.session = None 
        self.signature = None

        self.game_object = None 

        self.fetch_regions()
        # self.create_new_session()

    def fetch_regions(self):
        req_region = requests.get(self.main_url)
        soup = BeautifulSoup(req_region.text, 'html.parser')
        for lang in soup.select('div.lang-switcher > div.dropdown-lang > ul > li'):
            self.region[lang.find('a').text] = lang.find('a')['href']
    
    def show_regions(self):
        return self.region

    def select_region(self, name):
        if name not in self.region:
            raise Exception('Selected region name not found')
        else:
            self.base_url = self.region[name] 

    def create_new_session(self):
        if not self.base_url: raise Exception('Error creating new session, please select region first')
        with requests.Session() as request:
            req_main = request.get(self.base_url, headers=self.headers)
            translated_theme_name = re.search(
                r'"translated_theme_name":"(.*?)"', req_main.text).group(1)
            urlWs = re.search(r'"urlWs":"(.*?)"',
                            req_main.text).group(1).replace('\/', '/')
            subject_id = re.search(r'"subject_id":"(.*?)"', req_main.text).group(1)

            req_token = request.get(f'{self.base_url}/game', headers=self.headers)
            uid_ext_session = re.search(
                r"var uid_ext_session = '(.*?)'", req_token.text).group(1)
            frontaddr = re.search(r"var frontaddr = '(.*?)'",
                                req_token.text).group(1)

            timestamp = int(datetime.now().timestamp()) * 1000
            callback_string = self.jQuery + str(timestamp)
            req_session = request.get(
                f"{self.base_url}/new_session?callback={callback_string}&urlApiWs={urlWs}&player=website-desktop&partner=1&uid_ext_session={uid_ext_session}&frontaddr={frontaddr}&childMod=&constraint=ETAT<>'AV'&soft_constraint=&question_filter=&_={timestamp}",
                headers=self.headers
            ).text

            result = json.loads(
                req_session[req_session.find('(') + 1:req_session.rfind(')')])

            self.urlWs = urlWs
            self.frontaddr = frontaddr

            session_data = result['parameters']['step_information']
            self.game_object = session_data

            session_identification = result['parameters']['identification']
            self.channel = session_identification['channel']
            self.session = session_identification['session']
            self.signature = session_identification['signature']
    
    def show_question(self):
        return self.game_object

    def answer_question(self, answer):
        with requests.Session() as request:
            step = self.game_object['step']

            timestamp = int(datetime.now().timestamp()) * 1000
            callback_string = self.jQuery + str(timestamp)
            req_answer = request.get(
                f"https://id.akinator.com/answer_api?callback={callback_string}&urlApiWs={self.urlWs}&session={self.session}&signature={self.signature}&step={step}&frontaddr={self.frontaddr}&answer={answer}&question_filter=",
                headers=self.headers
            ).text

            result = json.loads(req_answer[req_answer.find('(') + 1:req_answer.rfind(')')])

            self.game_object = result['parameters']

            return self.game_object

    def end_question(self):
        with requests.Session() as request:
            step = self.game_object['step']

            timestamp = int(datetime.now().timestamp()) * 1000
            callback_string = self.jQuery + str(timestamp)
            req_win = request.get(
                f"{self.urlWs}/list?callback={callback_string}&session={self.session}&signature={self.signature}&step={step}",
                headers=self.headers
            ).text

            result = json.loads(req_win[req_win.find('(') + 1:req_win.rfind(')')])
            guess = result['parameters']['elements']

            return None if not guess else guess[0]['element']