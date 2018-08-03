#coding:utf-8

import requests
import json


class Collector:

    collect_url = 'http://zlal32teyptf4tvi.onion/json/all'
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'}

    def __init__(self,host,port):
        self.session = requests.session()
        socks_str = "socks5h://{}:{}".format(host,str(port))
        self.session.proxies = {'http':socks_str,'https:':socks_str}

    def get_link(self):
        res_json = self.session.get(Collector.collect_url,headers=Collector.header).text
        res_lst = json.loads(res_json)
        hs_lst = [hs_dict["hostname"] for hs_dict in res_lst]
        return list(set(hs_lst))

    def get_content(self,url):
        target_url = 'http://{}'.format(url)
        res_text = self.session.get(target_url,headers=Collector.header).text
        return res_text

