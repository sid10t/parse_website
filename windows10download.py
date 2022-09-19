import os
import re
import time
import socket
import requests
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

proxies = {
    'http': 'socks5://127.0.0.1:10808',
    'https': 'socks5://127.0.0.1:10808'
}


proxy = urllib.request.ProxyHandler({'https': '127.0.0.1:10809'})
open_proxy = urllib.request.build_opener(proxy)
urllib.request.install_opener(open_proxy)
socket.setdefaulttimeout(20)


def get_detail_urls(url):
    # url = 'https://www.windows10download.com/w10-audio-multimedia/software-1-0-d.html'
    
    # 获取页数
    # obj = re.compile(r"<li> \([0-9]+.*?pages\)</li>", re.S)
    # res = obj.finditer(resp.text)
    # for it in res:
    #     page_size = it.group().split('(')[-1].split('&')[0]
    #     break
    # 获取当前页的每个软件的 url
    obj = re.compile(r'[a-zA-z]+://[^\s]*/download.html', re.S)
    res = obj.finditer(requests.get(url, proxies=proxies).text)
    detail_urls = [it.group() for it in res]
    return detail_urls

def get_effective_url(url):
    # url = 'https://www.windows10download.com/thundersoft-gemplayer/download.html'
    obj = re.compile(r'http(|s)%253A%252F%252[^\s]*" rel="nofollow"', re.S)
    res = obj.finditer(requests.get(url, proxies=proxies).text)
    hrefs = [it.group().split('"')[0] for it in res]
    effective_urls = {}
    for href in hrefs:
        new_url = f"https://www.windows10download.com/rd.html?url={href}"
        response = requests.get(new_url, stream=True, timeout=30, proxies=proxies)
        # 判断是否为可下载文件
        if 'Content-Length' in response.headers.keys():
            effective_urls["name"] = url.split('/')[-2]+".zip"
            effective_urls["url"] = new_url
            break
    return effective_urls


def get_download_url(url):
    name = []
    urls = []
    d_urls = get_detail_urls(url)
    for o_url in d_urls:
        try:
            info = get_effective_url(o_url)
            if info != {}:
                name.append(info["name"])
                urls.append(info["url"])
                print(info["name"], info["url"])
        except:
            pass

    return name, urls


def download_zip(url, name):
    try:
        filepath = os.path.join(os.getcwd(), name)
        cc = 0
        start = time.time()
        while cc < 5:
            try:
                path, headers = urllib.request.urlretrieve(url, filepath)
                print()
                break

            except socket.timeout:
                cc += 1
                if (cc == 5): 
                    print(name, "ConnectionError --> END!\n")
                    raise Exception('4016 NETWORK TERRIBLE!')
                print(name, "ConnectionError", cc)
                time.sleep(30*cc)
            
        pe_size = int(headers['content-length']) / 1024 / 1024
        end = time.time()
        print(
            f'本地路径: \"{path}\" --> {pe_size:.2f} MB--> 用时 {(end - start):.2f} 秒 --> {url}')
        return True

    except urllib.error.ContentTooShortError as e:
        print(name + " ContentTooShortError: " + e.reason)

    except urllib.error.URLError:
        pass

    except Exception as e:
        print(e)
        print(f"收集失败  --> {url}")


if __name__ == '__main__':
    try:
        cnt = 0
        total = 0
        
        first = "Audio & Multimedia categories"
        size = 160
        base_url = 'https://www.windows10download.com/w10-audio-multimedia/software-1'
        basepath = os.path.join(os.getcwd(), first)
        if not os.path.exists(basepath):
            os.makedirs(basepath)

        for i in range(size):
            ogn_url = f"{base_url}-{i*20}-d.html"
            names, urls = get_download_url(ogn_url)
            with ThreadPoolExecutor(20) as pools:
                for i in range(len(names)):
                    try:
                        name = names[i]
                        url = urls[i]
                        pools.submit(lambda p: download_zip(*p), [url, basepath, name])

                    except UnboundLocalError:
                        pass

                    except Exception as e:
                        print(url)
                        print(e)
            
    except Exception as e:
        print("4001 MAIN ERROR!")
        print(e)

    finally:
        print(f"--> {cnt} {(cnt/len(urls)*100):.2f}% {(total/1024):.2f}GB <--\n")