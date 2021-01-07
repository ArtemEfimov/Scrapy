import scrapy
from ..utils import URL, cookie_parser, parse_url
from ..items import RealestateItem
from scrapy.loader import ItemLoader
import json


class ZillowSpider(scrapy.Spider):
    name = 'zillow'

    def start_requests(self):
        yield scrapy.Request(url=URL,
                             cookies=cookie_parser(),
                             callback=self.parse,
                             meta={'currentPage': 1})

    def parse(self, response):
        current_page = response.meta.get('currentPage')
        json_resp = json.loads(response.body)
        houses = json_resp.get('searchResults').get('listResults')
        for house in houses:
            loader = ItemLoader(item=RealestateItem())
            loader.add_value('id', house.get('id'))
            loader.add_value('imgSrc', house.get('imgSrc'))
            loader.add_value('statusType', house.get('statusType'))
            loader.add_value('statusText', house.get('statusText'))
            loader.add_value('price', house.get('price'))
            loader.add_value('address', house.get('address'))
            loader.add_value('beds', house.get('beds'))
            loader.add_value('baths', house.get('baths'))
            loader.add_value('area_sqft', house.get('area_sqft'))
            loader.add_value('latitude', house.get('latLong').get('latitude'))
            loader.add_value('longitude', house.get('latLong').get('longitude'))
            loader.add_value('brokerName', house.get('brokerName'))
            loader.add_value('brokerPhone', house.get('brokerPhone'))
            yield loader.load_item()

        total_pages = json_resp.get('searchList').get('totalPages')
        if current_page < total_pages:
            current_page += 1
            yield scrapy.Request(url=parse_url(url=URL, next_page_number=current_page), cookies=cookie_parser(),
                                 callback=self.parse,
                                 meta={'currentPage': current_page})
