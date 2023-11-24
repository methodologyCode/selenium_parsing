import re
from http import HTTPStatus
from random import choice

import requests
from bs4 import BeautifulSoup


def get_proxy():
    html = requests.get('https://free-proxy-list.net/').text
    soup = BeautifulSoup(html, 'lxml')

    trs = soup.find('tbody').find_all('tr')

    proxies = []

    for tr in trs:
        tds = tr.find_all('td')
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        schema = 'https' if 'yes' in tds[6].text.strip() else 'http'
        proxy = {'schema': schema, 'address': ip + ':' + port}
        proxies.append(proxy)

    return choice(proxies)


def get_csrf_token_and_cookies(proxy):
    url = 'https://www.maxmind.com/en/geoip2-precision-demo'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/101.0.0.0 Safari/537.36',
               }
    response = requests.get(url, headers=headers, proxies=proxy)
    soup = BeautifulSoup(response.text, 'html.parser')
    script = soup.find('div', id='geoip-demo').find_next_sibling('script').text
    pattern = r'window\.MaxMind\.X_CSRF_TOKEN = "(.*?)";'
    match = re.search(pattern, script)

    if match is None:
        raise Exception

    value = match.group(1)
    cookies = response.cookies.get_dict()
    return value, cookies


def get_ip_address(proxy):
    url = 'https://2ip.ru/'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/101.0.0.0 Safari/537.36',
               }
    response = requests.get(url, headers=headers, proxies=proxy)

    if response.status_code != HTTPStatus.OK:
        raise Exception

    soup = BeautifulSoup(response.text, 'html.parser')
    ip_address = soup.find('div', class_='ip').find('span').text
    return ip_address


def get_token(proxy):
    csrf, cookies = get_csrf_token_and_cookies(proxy)
    headers = {'x-csrf-token': csrf}
    response = requests.post('https://www.maxmind.com/en/geoip2/demo/token',
                             cookies=cookies, headers=headers, proxies=proxy)

    if response.status_code != 201:
        raise Exception

    token = response.json()['token']
    return token


def get_timezone(ip_address, proxy):
    url = f"https://geoip.maxmind.com/geoip/v2.1/city/{ip_address}?demo=1"
    headers = {'authorization': f"Bearer {get_token(proxy)}",
               'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/101.0.0.0 Safari/537.36',
               }
    response = requests.get(url, headers=headers, proxies=proxy)

    if response.status_code != HTTPStatus.OK:
        raise Exception

    return response.json()['location']['time_zone']


def get_regions(timezone, proxy):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/101.0.0.0 Safari/537.36',
               }
    url = 'https://gist.github.com/salkar/19df1918ee2aed6669e2'
    response = requests.get(url, headers=headers, proxies=proxy)

    if response.status_code != HTTPStatus.OK:
        raise Exception

    soup = BeautifulSoup(response.text, 'html.parser')
    regions = []
    table = soup.find('table', class_="highlight tab-size "
                                      "js-file-line-container "
                                      "js-code-nav-container "
                                      "js-tagsearch-file")
    tr = table.find_all('tr')
    for items in tr:
        for item in items.find_all('td'):
            if timezone in item.text:
                item = item.text.replace("[", "").replace("]", "").replace(",",
                                                                           "")
                regions.append(item.split('" "')[0].strip().replace('"', ''))

    return regions


def save_to_txt(timezone, regions):
    with open('result.txt', 'w') as file:
        file.write(timezone + '\n')
        if regions:
            file.write('\n'.join(regions))
        else:
            file.write("No regions found")
    return 'Готово'


proxies = get_proxy()
proxy = {proxies['schema']: proxies['address']}
ip_address = get_ip_address(proxy)
timezone = get_timezone(ip_address, proxy)
regions = get_regions(timezone, proxy)
print(save_to_txt(timezone, regions))

