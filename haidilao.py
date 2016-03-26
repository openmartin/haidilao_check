# -*- coding: utf-8 -*-
import requests
import yaml
import json
import time
from datetime import date
import logging
import logging.handlers

LOGIN_URL = 'http://cater.haidilao.com/Cater/wap/gotoWapLoginPage.action?to=personCenter'
LOGIN_ACTION = 'http://cater.haidilao.com/Cater/wap/login.action'

LOGOUT_URL = 'http://cater.haidilao.com/Cater/wap/loginout.action'

PERSON_CENTER_URL = 'http://cater.haidilao.com/Cater/wap/personCenter.action'

CHECK_URL = 'http://cater.haidilao.com/hdl-applet/views/template/web/signManage_sign.xhtml'
CHECK_ACTION = 'http://cater.haidilao.com/hdl-applet/rs/external/pointExtRest/addSignInfo'

YAML_CONF = 'config.yaml'

LOG_FILE = 'haidilao_check.log'

# 日志格式
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)   # 实例化formatter

# 日志文件handler
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=5)  # 实例化handler
handler.setFormatter(formatter)      # 为handler添加formatter

# console handler
console = logging.StreamHandler()
console.setFormatter(formatter)

logger = logging.getLogger('haidilao')    # 获取名为haidilao的logger
logger.addHandler(handler)           # 为logger添加handler
logger.addHandler(console)
logger.setLevel(logging.DEBUG)


class HttpCheck(object):

    def __init__(self):
        config = yaml.load(open(YAML_CONF))
        login = config.get('main', {}).get('login', {})
        self.user = login.get('user', '')
        self.password = login.get('password', '')
        self.userid = login.get('userid', '')
        self.customerid = login.get('customerid', '')

        self.session = requests.Session()
        self.is_login = False

    def login(self):
        r = self.session.get(LOGIN_URL)
        login_params = {'username': self.user, 'password': self.password}
        r = self.session.post(LOGIN_ACTION, data=login_params)
        resp_txt = r.text
        resp = json.loads(resp_txt)
        logger.info(resp_txt)
        if resp.get('message') == 'success':
            logger.info('login success')
            self.is_login = True
        else:
            logger.info('login failed')
            self.is_login = False

    def logout(self):
        logger.info('logout')
        logout_params = {'userid': self.customerid, 'ssoid': self.customerid}
        r = self.session.post(LOGOUT_URL, data=logout_params)
        resp_txt = r.text
        logger.info(resp_txt)

    def person_center(self):
        logger.info('person center')
        r = self.session.get(PERSON_CENTER_URL)

    def check(self):
        sign_params = {'param.userId': self.userid, 'param.userPhone': self.user}
        r = self.session.post(CHECK_URL, data=sign_params)

        headers = {'content-type': 'application/json',
                   'Host': 'cater.haidilao.com',
                   'Origin': 'http://cater.haidilao.com',
                   'Referer': 'http://cater.haidilao.com/hdl-applet/views/template/web/signManage_sign.xhtml',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
                   'X-Requested-With': 'XMLHttpRequest'}
        check_params = {'userId': self.userid, 'userPhone': self.user}
        r = self.session.post(CHECK_ACTION, data=json.dumps(check_params), headers=headers)
        resp_txt = r.text
        logger.info(resp_txt)
        resp = json.loads(resp_txt)


if __name__ == '__main__':
    http_bot = HttpCheck()
    http_bot.login()
    time.sleep(1)
    http_bot.person_center()
    time.sleep(2)
    http_bot.check()
    time.sleep(1)
    http_bot.logout()
