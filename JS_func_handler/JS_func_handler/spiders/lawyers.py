# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest


class LawyersSpider(scrapy.Spider):
    name = 'lawyers'
    start_urls = ['https://www.lw.com/people?searchIndex=B&esmode=1']

    script = '''
        function main(splash, args)
            splash.private_mode_enabled = false
            assert(splash:go(args.url))
            assert(splash:wait(5))
            assert(splash:runjs(args.js_source))
            assert(splash:wait(5))
            return splash:html()
        end
    '''

    def parse(self, response):
        # inspect_response(response, self)
        current_page = int(response.xpath("//a[@class='currentPage']/text()").get())
        lawyers_urls = response.xpath('//div[@class="tileName"]/a/@href').getall()
        for url in lawyers_urls:
            yield response.follow(url=url, callback=self.lawyer_data_parse)
        next_page_url = response.xpath('//a[@class="moveNextLink"]')
        if next_page_url is not None:
            next_page = current_page + 1
            np_js = f"javascript:__doPostBack('ctl00$ctl00$ContentPlaceHolder1$MainContentPlaceHolder$PagerControl1','{next_page}')"
            yield SplashRequest(url=response.url, callback=self.parse, endpoint='execute',
                                args={'lua_source': self.script,
                                      'js_source': np_js},
                                dont_filter=True)

    def lawyer_data_parse(self, response):
        name = response.xpath('//div[@id="BusinessCardPanel"]/h1/text()').get()
        yield {
            'name': name
        }
