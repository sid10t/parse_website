import os
import socket
import requests
import urllib.request
from lxml import etree
from concurrent.futures import ThreadPoolExecutor

headers = {
    "User-Agent" : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:75.0) Gecko/20100101 Firefox/75.0'
}

PROXY = '127.0.0.1:10809'

proxies = {
    'http': 'socks5://127.0.0.1:10808',
    'https': 'socks5://127.0.0.1:10808'
}

proxy = urllib.request.ProxyHandler({'https': PROXY})
open_proxy = urllib.request.build_opener(proxy)
urllib.request.install_opener(open_proxy)
socket.setdefaulttimeout(20)

def get_detail_urls(url):
    html = etree.HTML(requests.get(url, headers=headers, proxies=proxies).text)
    lis = html.xpath("/html/body/div[2]/div/main/ul/li")
    urls = []
    for li in lis:
        urls.append(li.xpath("./article/h3/a/@href")[0].replace("/windows", "/download"))
    return urls
    
def get_info(url):
    html = etree.HTML(requests.get(url, headers=headers, proxies=proxies).text)
    new_url = html.xpath("/html/body/div[2]/div/div[1]/main/div/section[1]/ul[1]/li[1]/a/@href")[0]
    new_html = etree.HTML(requests.get(new_url, headers=headers, proxies=proxies).text)
    down_url = new_html.xpath("/html/body/div[3]/div[2]/div/div[1]/div/ul/li[1]/a/@href")[0]
    name = new_html.xpath("/html/body/div[3]/div[3]/dl/dd[1]/text()")[0]
    info = {"name":name, "url":down_url}
    return info

def download(url, basePath):
    info = get_info(url)
    path = os.path.join(basePath, info['name'])
    print(path)
    with open(path, "wb") as f:
        f.write(requests.get(info['url'], headers=headers, proxies=proxies).content)

if __name__ == '__main__':
    basePath = os.path.join(os.getcwd(), "Audio & Video")
    size = 5
    if not os.path.exists(basePath):
        os.makedirs(basePath)
    with ThreadPoolExecutor(20) as pools:
        for i in range(1, size+1):
            baseURL = f"https://en.lo4d.com/windows/audio-video-software/{i}"
            urls = get_detail_urls(baseURL)
            for url in urls:
                try:
                    pools.submit(lambda p: download(*p), [url, basePath])

                except UnboundLocalError:
                    pass

                except Exception as e:
                    print(e)


