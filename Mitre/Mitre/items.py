# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MitreItem(scrapy.Item):
    # define the fields for your item here like:
    techniques = scrapy.Field()
    sub_techniques = scrapy.Field()
    url = scrapy.Field()
    url1 = scrapy.Field()
    reference_domain = scrapy.Field()
    reference_link = scrapy.Field()

