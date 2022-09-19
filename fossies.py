import os
import socket
import requests
import urllib.request
from lxml import etree

PROXY = '127.0.0.1:10809'

proxies = {
    'http': 'socks5://127.0.0.1:10808',
    'https': 'socks5://127.0.0.1:10808'
}

headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
}

proxy = urllib.request.ProxyHandler({'https': PROXY})
open_proxy = urllib.request.build_opener(proxy)
urllib.request.install_opener(open_proxy)
socket.setdefaulttimeout(20)

def get_down_urls():
    try:
        down_urls = []
        url = 'https://fossies.org/windows/misc/'
        html = etree.HTML(requests.get(url, proxies=proxies).text)
        trs = html.xpath('//*[@id="archlist"]/table/tr')
        for tr in trs:
            href = tr.xpath('td/a')[0].get('href')
            down_urls.append(url+href)
        return down_urls
    except:
        pass

def download(url, name):
    try:
        filepath = os.path.join(os.getcwd(), name)
        urllib.request.urlretrieve(url, filepath)

    except Exception as e:
        print(e)
        
if __name__ == '__main__':
    urls = get_down_urls()
    for url in urls:
        try:
            name = url.split('/')[-1]
            download(url, name)
        except Exception as e:
            print(e)