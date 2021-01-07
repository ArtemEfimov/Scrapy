# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.shell import inspect_response

import scrapy
from scrapy.utils.project import get_project_settings


class ParsedirectorySpider(scrapy.Spider):
    name = 'ParseDirectory'
    start_urls = ['https://www.datadiction.com.au/bin/dd.dll/Lincs?xps&MBR=MEL']

    @staticmethod
    def normalize(value: str) -> str:
        return value.replace('\xa0', '')

    def parse(self, response):
        uls = response.xpath('//ul')[:3]
        urls = []
        [urls.extend(cat.xpath('./li/a')) for cat in uls]
        for url in urls:
            category = url.xpath('./text()').get()
            category_link = url.xpath('./@href').get()
            # if category == 'Women   ':
            yield response.follow(url=category_link, callback=self.category_parse,
                                      meta={'category': category})
            # else:
            #     pass

    def category_parse(self, response):
        if not response.xpath('//ul[@class="browse"]'):
            subcategories_ul = response.xpath('//ul[@class="svcList"]/li')
            sub_category_links = [li.xpath('./a/@href').get() for li in subcategories_ul]
            for link in sub_category_links:
                yield response.follow(url=link, callback=self.council_services_categorie_parse)

        else:
            category = response.meta.get('category')
            sub_category = response.meta.get('sub_category')
            subcategories_ul = response.xpath('//ul[@class="browse"]/li')
            sub_category_links = [li.xpath('./a/@href').get() if li.xpath('./a/@href').get() is not None else
                                  li.xpath('./small/a/@href').get() for li in subcategories_ul]
            if category == 'Emergency Services':
                for li in sub_category_links:
                    yield response.follow(url=li, callback=self.emergency_services_category_parse,
                                          meta={'category': category})
            else:
                for li in sub_category_links:
                    yield response.follow(url=li, callback=self.other_sub_categoties_parse,
                                          meta={'category': category,
                                                'sub_category': sub_category})

    def emergency_services_category_parse(self, response):
        category = response.meta.get('category')
        sub_category = response.xpath('//div[@class="srchHdr"]/text()').get()
        additional_url = response.xpath('//div[@id="content"]/p[2]/a/@href').get()
        if additional_url is not None:
            sub_sub_category = response.xpath('//p[2]/a/text()').get().split(':')[0]
            yield response.follow(url=additional_url, callback=self.add_web_or_in_home_services_parse,
                                  meta={'category': category, 'sub_category': sub_category,
                                        'sub_sub_category': sub_sub_category})
        urls = []
        [urls.extend(li.xpath('.//li/a/@href').getall()) for li in response.xpath('//ul[@class="svcList"]')]
        for url in urls:
            sub_sub_category = 'none'
            yield response.follow(url=url, callback=self.sub_sub_categories_parse,
                                  meta={'category': category, 'sub_category': sub_category,
                                        'sub_sub_category': sub_sub_category}, dont_filter=True)

    def council_services_categorie_parse(self, response):
        category = 'Council Services'
        sub_category = 'none'
        sub_sub_category = 'none'
        title = response.xpath('//div[@class="fullrec"]/h2/text()').get()
        _type = response.xpath('//p[contains(., "Web:")]/a/@href').get()
        if not _type:
            _type = 'none'
        description = response.xpath('//p[contains(., "Description:")]/text()').get()
        area_served = response.xpath('//p[contains(., "Area Served:")]/text()').get()
        keywords = self.normalize(response.xpath('//p[contains(., "Keywords:")]/text()').get())

        yield {
            'category': category,
            'sub_category': sub_category,
            'sub_sub_category': sub_sub_category,
            'title': title,
            'Type': _type,
            'description': description,
            'area_served': area_served,
            'keywords': keywords
        }

    def other_sub_categoties_parse(self, response):
        # inspect_response(response, self)
        if (response.meta.get('category') and response.meta.get('sub_category')) is not None:
            category = response.meta.get('category')
            sub_category = response.meta.get('sub_category')
            sub_sub_category = response.xpath('//div[@class="srchHdr"]/text()[2]').get().replace(' / ', '')
            additional_url = response.xpath('//div[@id="content"]/p[2]/a/@href').get()
            urls = response.xpath('//ul[@class="svcList"]/li/a/@href').getall()
            if additional_url is not None and not response.meta.get('additional_url_text'):
                yield response.follow(url=additional_url, callback=self.add_web_or_in_home_services_parse,
                                      meta={'category': category, 'sub_category': sub_category,
                                            'sub_sub_category': sub_sub_category})
            for url in urls:
                yield response.follow(url=url, callback=self.sub_sub_categories_parse,
                                      meta={'category': category, 'sub_category': sub_category,
                                            'sub_sub_category': sub_sub_category}, dont_filter=True)
            next_page = response.xpath('//div[@class="paging"]/a/text()').get()
            if next_page == 'next page':
                additional_url_text = response.xpath('//div[@id="content"]/p[2]/a/text()').get()
                next_page_url = response.xpath('//div[@class="paging"]/a/@href').get()
                yield response.follow(url=next_page_url, callback=self.other_sub_categoties_parse, dont_filter=True,
                                      meta={'additional_url_text': additional_url_text, 'category': category,
                                            'sub_category': sub_category,
                                            'sub_sub_category': sub_sub_category})

        elif not (response.meta.get('category') and response.meta.get('sub_category')):
            category = response.xpath('//div[@class="srchHdr"]/a/text()').get()
            if category is not None:
                sub_category = response.xpath('//div[@class="srchHdr"]/text()').get().replace(' / ', '')
                sub_sub_category = 'none'
                additional_url = response.xpath('//div[@id="content"]/p[2]/a/@href').get()
                urls = response.xpath('//ul[@class="svcList"]/li/a/@href').getall()
                if additional_url is not None and not response.meta.get('additional_url_text'):
                    add_sub_sub_category = response.xpath('//p[2]/a/text()').get().split(':')[0]
                    yield response.follow(url=additional_url, callback=self.web_or_in_home_services_parse,
                                          meta={'category': category, 'sub_category': sub_category,
                                                'add_sub_sub_category': add_sub_sub_category})

                for url in urls:
                    yield response.follow(url=url, callback=self.sub_sub_categories_parse,
                                          meta={'category': category, 'sub_category': sub_category,
                                                'sub_sub_category': sub_sub_category}, dont_filter=True)
                next_page = response.xpath('//div[@class="paging"]/a/text()').get()
                if next_page == 'next page':
                    additional_url_text = response.xpath('//div[@id="content"]/p[2]/a/text()').get()
                    next_page_url = response.xpath('//div[@class="paging"]/a/@href').get()
                    yield response.follow(url=next_page_url, callback=self.other_sub_categoties_parse, dont_filter=True,
                                          meta={'additional_url_text': additional_url_text})
            else:
                category = response.xpath('//div[@class="bc"]/a/text()').get()
                sub_category = response.xpath('//div[@class="bc"]/a[2]/text()').get()
                url = response.url
                yield response.follow(url=url, callback=self.category_parse,
                                      meta={'category': category, 'sub_category': sub_category
                                            }, dont_filter=True)

    def web_or_in_home_services_parse(self, response):
        category = response.meta.get('category')
        sub_category = response.meta.get('sub_category')
        sub_sub_category = response.meta.get('add_sub_sub_category')
        urls = response.xpath('//ul/li/a/@href').getall()
        for url in urls:
            yield response.follow(url=url, callback=self.sub_sub_categories_parse,
                                  meta={'category': category, 'sub_category': sub_category,
                                        'sub_sub_category': sub_sub_category}, dont_filter=True)

    def add_web_or_in_home_services_parse(self, response):
        category = response.meta.get('category')
        sub_category = response.meta.get('sub_category')
        sub_sub_category = response.meta.get('sub_sub_category')
        urls = response.xpath('//ul/li/a/@href').getall()
        for url in urls:
            yield response.follow(url=url, callback=self.sub_sub_categories_parse,
                                  meta={'category': category, 'sub_category': sub_category,
                                        'sub_sub_category': sub_sub_category}, dont_filter=True)

    def sub_sub_categories_parse(self, response):
        category = response.meta['category']
        sub_category = response.meta['sub_category']
        sub_sub_category = response.meta['sub_sub_category']
        title = response.xpath('//div[@class="fullrec"]/h2/text()').get().replace('�', "'")
        _type = response.xpath('//p[contains(., "Web:")]/a/@href').get()
        if not _type:
            _type = 'none'
        description = response.xpath('normalize-space(//p[contains(., "Description:")]/text())').get().replace(
            r'\r\n�\t', ', ').replace('�', '').replace('', '')
        area_served = response.xpath('//p[contains(., "Area Served:")]/text()').get()
        keywords = self.normalize(response.xpath('normalize-space(//p[contains(., "Keywords:")]/text())').get())

        yield {
            'category': category,
            'sub_category': sub_category,
            'sub_sub_category': sub_sub_category,
            'title': title,
            'Type': _type,
            'description': description,
            'area_served': area_served,
            'keywords': keywords
        }


#  Category, Subcategory, Subsubcategory, Title, Type(e.g. website), Description, Area Served, Keywords
if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(ParsedirectorySpider)
    process.start()

# //div[@id="content"]/p[2]    Phone, web or in-home services: 4.
# https://www.datadiction.com.au/bin/dd.dll/Lincs?xps3&mbr=MEL&a=10&gid=6153&d=230&ds=1077>
# 'category': "Children's and Family Services", 'sub_category': ' / Toy Libraries', 'sub_sub_category': 'Toy Libraries',
