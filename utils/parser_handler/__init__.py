import requests
from bs4 import BeautifulSoup
from requests.exceptions import InvalidSchema
from fake_useragent import UserAgent
from utils.proxy import init_proxy
from utils.paths.chromedriver_path import path

def init_crawler(url, proxy=False):
    try:
        ua = UserAgent()
        headers = { 'User-Agent' : ua.random }
        
        if proxy:
            proxy = init_proxy(path)
            proxyList = { "http": "http://" + proxy}
            page = requests.get(url, headers=headers, proxies=proxyList)

        else:
            page = requests.get(url, headers=headers)

        if page.status_code != 200:
            print(f'[ERRO {page.status_code}] Site indisponivel, tente novamente mais tarde')
            return

        return BeautifulSoup(page.text, "lxml")

    except InvalidSchema:
        print('Algo deu errado!')
        return

    except ConnectionError:
        print('Não conseguiu se conectar na página!')
        return


def init_parser(html):
    return BeautifulSoup(html, "lxml")


def remove_duplicates(data):
    return list(dict.fromkeys(data))

