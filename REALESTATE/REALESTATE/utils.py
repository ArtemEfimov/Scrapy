"""Some additional functions"""

import json
from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
import logging

logging.basicConfig(level='DEBUG')
logger = logging.getLogger('Zillow')

URL = 'https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState={"pagination":{},' \
      '"usersSearchTerm":"Miami, FL","mapBounds":{"west":-80.43908475805662,"east":-80.05559324194334,' \
      '"south":25.71035417113481,"north":25.83495013143864},"regionSelection":[{"regionId":12700,"regionType":6}],' \
      '"isMapVisible":true,"mapZoom":12,"filterState":{"sort":{"value":"globalrelevanceex"}},"isListVisible":true} '


def cookie_parser():
    """Parse cookie to inject into request"""
    cookies_string = 'zguid=23|%245cc0fc4a-4f94-47d4-bab7-e3e895c0c580; ' \
                     'search=6|1596895175241%7Crect%3D26.276158170416835%252C-79.48035596777342%252C25.26703349341841' \
                     '%252C-81.01432203222654%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D0%26pt%3Dpmf%252Cpf%26fs%3D1' \
                     '%26fr%3D0%26mmm%3D1%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0' \
                     '%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview' \
                     '%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0' \
                     '%263dhome%3D0%09%0912700%09%09%09%09%09%09; G_ENABLED_IDPS=google; ' \
                     'zgsession=1|5a3eec47-fb77-4f95-b852-893f37a069d1; ' \
                     'AWSALB=r+A2dZdLqzEnzBLFBnnCNkHwTLvn6UPE9CtKNhK+/Tmb1z/5mh1RmISjKCeK41nO8xYUi9' \
                     '/Z7xTsNENUM99ITZGFJE+sA3u0E7O0JDDvFIx9MxXErKY+ppPGzG4K; ' \
                     'AWSALBCORS=r+A2dZdLqzEnzBLFBnnCNkHwTLvn6UPE9CtKNhK+/Tmb1z/5mh1RmISjKCeK41nO8xYUi9' \
                     '/Z7xTsNENUM99ITZGFJE+sA3u0E7O0JDDvFIx9MxXErKY+ppPGzG4K; ' \
                     'JSESSIONID=46B334AD38A25EDA7FBE334CD90A99AF; g_state={"i_p":1594212243486,"i_l":1}; ' \
                     '_pxvid=1e17f3a4-c10c-11ea-a973-0242ac120008 '
    cookie = SimpleCookie()
    cookie.load(cookies_string)
    # print(cookie.items())
    cookies = {k: v.value for k, v in cookie.items()}

    return cookies


def parse_url(url: str, next_page_number: int) -> str:
    """Pagination logic"""
    url_parsed = urlparse(url)
    # logger.info(url_parsed.query)
    query_string = parse_qs(url_parsed.query)
    # logger.info(query_string)
    pagination_value = json.loads(query_string.get('searchQueryState')[0])
    pagination_value['pagination'] = {'currentPage': next_page_number}
    query_string.get('searchQueryState')[0] = pagination_value
    # logger.info(query_string)
    encoded_qs = urlencode(query_string, doseq=True)
    # logger.info(encoded_qs)
    new_url = f'https://www.zillow.com/search/GetSearchPageState.htm?{encoded_qs}'
    # logger.info(new_url)
    return new_url


parse_url(URL, 6)
