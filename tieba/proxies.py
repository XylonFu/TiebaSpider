import threading
import time

import requests


class ProxyManager:
    def __init__(self, settings):
        # API相关设置
        self.proxy_api_url = "http://api.tianqiip.com/getip"
        self.white_api_url = "http://api.tianqiip.com/white/fetch"
        self.add_white_api_url = "http://api.tianqiip.com/white/add"

        # API认证信息
        self.secret = settings.get('PROXY_API_SECRET')
        self.sign = settings.get('PROXY_API_SIGN')
        self.key = settings.get('PROXY_API_KEY')

        # 代理状态信息
        self.current_proxy = None
        self.last_switch_time = time.time()

        # 控制参数
        self.proxy_valid_duration = 180
        self.last_retry_time = 0
        self.update_threshold = 10

        # 线程同步
        self.lock = threading.Lock()
        self.is_changing_proxy = False

    def fetch_public_ip(self):
        response = requests.get("https://www.ipplus360.com/getIP")
        ip_data = response.json()
        if ip_data['success'] and ip_data['code'] == 200:
            return ip_data.get('data', None)
        return None

    def is_ip_in_white_list(self, ip):
        params = {
            'key': self.key,
            'sign': self.sign,
            'brand': 2,
            'ip': ip,
        }
        response = requests.get(self.white_api_url, params=params)
        data = response.json()
        if data['code'] == 200 and data.get('data'):
            if ip in data['data']:
                return True
        return False

    def add_ip_to_white_list(self, ip):
        params = {
            'key': self.key,
            'sign': self.sign,
            'brand': 2,
            'ip': ip,
        }
        response = requests.get(self.add_white_api_url, params=params)
        data = response.json()
        if data['code'] == 200:
            return True
        return False

    def get_new_proxy(self, force=False):
        with self.lock:
            if self.is_changing_proxy:
                return
            self.is_changing_proxy = True
        try:
            public_ip = self.fetch_public_ip()
            if public_ip and not self.is_ip_in_white_list(public_ip):
                self.add_ip_to_white_list(public_ip)
            params = {
                'secret': self.secret,
                'num': 1,
                'type': 'json',
                'port': 2,
                'time': 3,
                'mr': 1,
                'sign': self.sign,
            }
            response = requests.get(self.proxy_api_url, params=params)
            data = response.json()
            if data['code'] == 1000 and data['data']:
                proxy_data = data['data'][0]
                self.current_proxy = "{}:{}".format(proxy_data['ip'], proxy_data['port'])
                self.last_switch_time = time.time()
                if force:
                    self.last_retry_time = time.time()
            else:
                self.current_proxy = None
        finally:
            with self.lock:
                self.is_changing_proxy = False

    def get_proxy(self):
        current_time = time.time()
        if not self.current_proxy or current_time - self.last_switch_time > self.proxy_valid_duration:
            self.get_new_proxy()
        return self.current_proxy
