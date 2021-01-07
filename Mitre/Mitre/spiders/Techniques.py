

# -*- coding: utf-8 -*-
import scrapy
from ..items import MitreItem



class TechniquesSpider(scrapy.Spider):
    name = 'Techniques'
    allowed_domains = ['attack.mitre.org']
    start_urls = ['https://attack.mitre.org']

    def parse(self, response):
        """
        Function scrape Enterprise Techniques
        """

        # get techniques  e.g 'Active Scanning'
        techniques = response.xpath('//tr[@class="technique-row"]')

        # loop over the techniques .
        # Fetch urls [https://attack.mitre.org/techniques/T1595/, https://attack.mitre.org/techniques/T1583/] and so on.

        for technique in techniques:
            technique_url = technique.xpath('.//a/@href').get()
            yield scrapy.Request(url=f'https://attack.mitre.org{technique_url}',
                                 callback=self.techniques_parse)

    def techniques_parse(self, response):
        """
        Function scrape techniques data
        total quantity is 205 techniques
        """

        item = MitreItem()
        reference_links = response.xpath('//span[@class="scite-citation-text"]/a')
        for link in reference_links:
            reference_link = link.xpath('.//@href').get()  # https://documents.trendmicro.com/assets/wp/wp-criminal-hideouts-for-lease.pdf  e.t.c.
            reference_domain_raw = link.xpath('.//@href').get().split('/')[2].split('.')[-1: -3: -1]
            reference_domain = '.'.join(reversed(reference_domain_raw))

            item['techniques'] = response.xpath('normalize-space(//div[@class="container-fluid"]/h1/text())').get()
            item['sub_techniques'] = 'None'
            item['url'] = response.xpath('//div[@class="card-data"]/text()').get()
            item['url1'] = response.url
            item['reference_domain'] = reference_domain
            item['reference_link'] = reference_link
            yield item

        # 4404 ---> item scraped with dont_filter = True
        # 4047  --> without dont_filter = True

        sub_techniques_links = response.xpath('//div[@class="card-data"][2]/a')    # for example: /techniques/T1595/001
        for link in sub_techniques_links:
            sub_technique_link = link.xpath('.//@href').get()
            yield response.follow(url=f'https://attack.mitre.org{sub_technique_link}',
                                  callback=self.sub_techs_parse, dont_filter=True)

    def sub_techs_parse(self, response):
        item = MitreItem()
        technique = response.xpath('//div[@class="container-fluid"][1]/h1/span/text()').get().replace(':', '')
        sub_technique = response.xpath('//div[@class="container-fluid"][1]/h1/text()').getall()[-1].strip()
        url = response.xpath('//div[@class="card-data"][1]/text()').get()
        url1 = response.url
        reference_links = response.xpath('//span[@class="scite-citation-text"]/a')
        for link in reference_links:
            reference_link = link.xpath('.//@href').get()  # https://documents.trendmicro.com/assets/wp/wp-criminal-hideouts-for-lease.pdf  e.t.c.
            reference_domain_raw = link.xpath('.//@href').get().split('/')[2].split('.')[-1: -3: -1]
            reference_domain = '.'.join(reversed(reference_domain_raw))
            item['reference_domain'] = reference_domain
            item['reference_link'] = reference_link
            item['techniques'] = technique
            item['sub_techniques'] = sub_technique
            item['url'] = url
            item['url1'] = url1

            yield item
            # 9532
