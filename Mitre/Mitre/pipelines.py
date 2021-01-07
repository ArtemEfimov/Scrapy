# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
# from scrapy.exceptions import DropItem


class MitrePipeline:
    def __init__(self):
        self.headers = False
        # self.ids_seen = set()

    def open_spider(self, spider):
        self.file = open('/home/artyom/Desktop/1.csv', 'w')
        pass

    def close_spider(self, spider):
        self.file.close()
        pass

    def process_item(self, item, spider):
        if not self.headers:
            headers_keys = ['techniques', 'sub_techniques', 'url', 'url1', 'reference_domain', 'reference_link']
            writer = csv.writer(self.file)
            writer.writerow(headers_keys)
            self.headers = True
        writer = csv.writer(self.file)
        writer.writerow([item['techniques'], item['sub_techniques'], item['url'], item['url1'],
                         item['reference_domain'], item['reference_link']])
        return item
