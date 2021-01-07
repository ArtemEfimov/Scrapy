"""Define here the models for your scraped items

See documentation in:
https://docs.scrapy.org/en/latest/topics/items.html
"""

from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst, MapCompose


def get_baths(bath: str) -> int:
    """Normalize output"""
    return int(bath)


class RealestateItem(Item):
    """Items"""
    id = Field(output_processor=TakeFirst())
    imgSrc = Field(output_processor=TakeFirst())
    statusType = Field(output_processor=TakeFirst())
    statusText = Field(output_processor=TakeFirst())
    price = Field(output_processor=TakeFirst())
    address = Field(output_processor=TakeFirst())
    beds = Field(output_processor=TakeFirst())
    baths = Field(
        input_processor=MapCompose(get_baths),
        output_processor=TakeFirst()
    )
    area_sqft = Field(output_processor=TakeFirst())
    latitude = Field(output_processor=TakeFirst())
    longitude = Field(output_processor=TakeFirst())
    brokerName = Field(output_processor=TakeFirst())
    brokerPhone = Field(output_processor=TakeFirst())
