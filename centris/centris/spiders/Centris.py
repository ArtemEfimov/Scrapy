# -*- coding: utf-8 -*-

import json
import scrapy
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class CentrisSpider(scrapy.Spider):
    name = 'Centris'
    query = {
        "query": {
            "UseGeographyShapes": 0,
            "Filters": [
                {
                    "MatchType": "CityDistrictAll",
                    "Text": "Montréal (All boroughs)",
                    "Id": 5
                }
            ],
            "FieldsValues": [
                {
                    "fieldId": "CityDistrictAll",
                    "value": 5,
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "SellingType",
                    "value": "Rent",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "Category",
                    "value": "Residential",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "LandArea",
                    "value": "SquareFeet",
                    "fieldConditionId": "IsLandArea",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "RentPrice",
                    "value": 0,
                    "fieldConditionId": "ForRent",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "RentPrice",
                    "value": 1500,
                    "fieldConditionId": "ForRent",
                    "valueConditionId": ""
                }
            ]
        },
        "isHomePage": True
    }
    unlock = {"uc": 4, "uck": "698445fc-8ce2-4b1f-b691-07b3fb0dbdfb"}
    position = {"startPosition": 0}
    script = """
                function main(splash, args)
                  splash:on_request(function(request)
                    if request.url:find('css') then
                      request.abort()
                    end
                  end)
                  splash.images_enabled = false
                  splash.js_enabled = false  
                  assert(splash:go(args.url))
                  assert(splash:wait(0.5))
                  return splash:html()
                end
             """
    # for scrapy- splash cluster
    http_user = 'user'
    http_pass = 'userpass'

    def start_requests(self):
        yield scrapy.Request(url='https://www.centris.ca/en', callback=self.unlock_requests)

    def unlock_requests(self, response):
        yield scrapy.Request(url='https://www.centris.ca/UserContext/UnLock',
                             method='POST',
                             body=json.dumps(self.unlock),
                             headers={'Content-Type': 'application/json'},
                             callback=self.update_query)

    def update_query(self, response):
        yield scrapy.Request(url='https://www.centris.ca/property/UpdateQuery',
                             method='POST',
                             body=json.dumps(self.query),
                             headers={'Content-Type': 'application/json'},
                             callback=self.get_inscription)

    def get_inscription(self, response):
        yield scrapy.Request(url='https://www.centris.ca/Property/GetInscriptions',
                             method='POST',
                             body=json.dumps(self.position),
                             headers={'Content-Type': 'application/json'},
                             callback=self.parse)

    def parse(self, response):
        r_dict = json.loads(response.body)
        html = r_dict.get('d').get('Result').get('html')
        # with open('index.html', 'w') as f:
        #     f.write(html)
        sel = Selector(text=html)
        urls = sel.xpath('//div[@class="thumbnail property-thumbnail"]/a/@href').getall()
        for url in urls:
            # yield response.follow(url=url,
            #                       callback=self.parse_category,
            #                       )
            abs_url = f'https://www.centris.ca{url}'
            yield SplashRequest(url=abs_url,
                                endpoint='execute',
                                callback=self.parse_category,
                                args={
                                    'lua_source': self.script
                                })
        count = r_dict.get('d').get('Result').get('count')
        inc_number_per_page = r_dict.get('d').get('Result').get('inscNumberPerPage')
        if self.position['startPosition'] <= count:
            self.position['startPosition'] += inc_number_per_page
            yield scrapy.Request(url='https://www.centris.ca/Property/GetInscriptions',
                                 method='POST',
                                 body=json.dumps(self.position),
                                 headers={
                                     'Content-Type': 'application/json',
                                 },
                                 callback=self.parse
                                 )

    def parse_category(self, response):
        name = response.xpath('//div[@class="brokerid col-7 col-sm-5"]/p/a/span/text()').get()
        yield {'name': name}


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(CentrisSpider)
    process.start()
