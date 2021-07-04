from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from utils.build import resource_path
from utils.proxy import init_proxy
from utils.paths.chromedriver_path import path


def setSelenium(console=True, proxy=False):
    # configuração do selenium
    chrome_options = Options()
    ua = UserAgent()
    userAgent = ua.random

    if not console:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

    # Desabilitar notificações
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    # evitar detecção anti-bot
    # chrome_options.add_argument(f'user-agent={userAgent}')
    chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36')
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("detach", True)
    # desabilitar o log do chrome
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    path = resource_path("C:\Selenium\chromedriver.exe")

    if proxy:
        PROXY = init_proxy(path)
        chrome_options.add_argument('--proxy-server=%s' % PROXY)

    return webdriver.Chrome(chrome_options=chrome_options, executable_path=path, service_log_path='NUL')
