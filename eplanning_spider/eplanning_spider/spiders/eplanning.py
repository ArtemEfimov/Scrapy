# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request, FormRequest


class EplanningSpider(Spider):
    name = 'eplanning'
    allowed_domains = ['eplanning.ie']
    start_urls = ['http://eplanning.ie/']

    def parse(self, response):
        urls = response.xpath('//a/@href').extract()
        for url in urls[1:2]:
            if url == '#': pass
            yield response.follow(url, callback=self.parse_app)

    def parse_app(self, response):
        app_url = response.xpath(
            '//*[@class="glyphicon glyphicon-inbox btn-lg"]/following-sibling::a/@href').extract_first()
        # data = response.xpath('//*[@class="glyphicon glyphicon-inbox btn-lg"]/following::a/@href').extract_first()
        # data = response.xpath('//*[@class="glyphicon glyphicon-inbox btn-lg"]/following-sibling::a[1]/@href').extract_first()
        yield Request(response.urljoin(app_url), callback=self.parse_form)
        # yield response.follow(app_url, callback=self.parse_form)

    def parse_form(self, response):
        yield FormRequest.from_response(response,
                                        formdata={'RdoTimeLimit': '42'},
                                        dont_filter=True,
                                        formxpath='(//form)[2]',
                                        callback=self.parse_page)

    def parse_page(self, response):
        app_urls = response.xpath('//td/a/@href').extract()
        for url in app_urls:
            yield response.follow(url, callback=self.parse_items)
        next_page_url = response.xpath('//*[@rel="next"]/@href').extract_first()
        # yield Request(response.urljoin(next_page_url), callback=self.parse_page)
        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse_page)

    def parse_items(self, response):
        agents_btn = response.xpath('//*[@title="Show Agents Popup"]/@style').extract_first()
        if 'display: inline;  visibility: visible;' in agents_btn:
            name = response.xpath('//tr[th="Name :"]/td/text()').extract_first().strip()
            address = response.xpath('//tr[th="Name :"]/following-sibling::tr/td/text()').extract()[0:3]
            phone = response.xpath('//tr[th="Phone :"]/td/text()').extract_first()
            if not phone or phone == ' ':
                phone = 'No phone'
            fax = response.xpath('//tr[th="Fax :"]/td/text()').extract_first()
            if not fax or fax == ' ':
                fax = 'No fax'
            email = response.xpath('//tr[th="e-mail :"]/td/text()').extract_first()
            if not email or email == ' ' or email == '  ':
                email = 'No e-mail'
            yield {'name': name,
                   'address': address,
                   'phone': phone,
                   'fax': fax,
                   'email': email}
        else:
            self.logger.info('Agent button not found on this page. Passing invalid url.')
