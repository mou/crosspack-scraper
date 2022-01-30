import os
import sys

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging


class MenuItem(scrapy.Item):
    title = scrapy.Field()
    attributes = scrapy.Field()
    ingredients = scrapy.Field()
    photo = scrapy.Field()
    photo_thumb = scrapy.Field()


class CrosspackSpider(scrapy.Spider):
    name = "crosspack"
    start_urls = [
        "https://crosspack.ru/",
    ]
    downloaded_items = 0

    def parse(self, response, **kwargs):
        for menu_section in response.css("form.radio-group label"):
            section_id = menu_section.css("input[name=products]::attr(value)").get()
            section_title = menu_section.css(".radio-group__label::text").get()
            for menu_item in response.css(f"div.products div.product[data-value=\"{section_id}\"]"):
                menu_item_page = menu_item.css("a.product__title::attr(href)").get()
                menu_item_thumbnail = menu_item.css("img.product__img::attr(src)").get()
                if self.downloaded_items > 0:
                    break
                self.downloaded_items += 1
                yield response.follow(menu_item_page, callback=self.parse_menu_item,
                                      cb_kwargs={"section_id": section_id,
                                                 "section_title": section_title,
                                                 "item_thumbnail": menu_item_thumbnail})

    def parse_menu_item(self, response, section_id, section_title, item_thumbnail):
        item_card = response.css("div.card__main")
        item_title = item_card.css("h1::text").get()
        item_attributes = dict([(param.css(".card__parameter-label::text").get(),
                                 param.css(".card__parameter-value::text").get())
                                for param in item_card.css(".card__parameter")])
        item_ingredients = item_card.css(".card__description p::text").get()
        item_photo_url = response.css(".card__illustration::attr(src)").get()
        yield {
            "section_title": section_title,
            "section_id": section_id,
            "title": item_title,
            "attibutes": item_attributes,
            "ingredients": item_ingredients,
            "photo": item_photo_url,
            "thumb": item_thumbnail,
        }


def main():
    cwd = os.path.abspath(os.path.curdir)
    download_dir = os.path.join(cwd, "files")
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)
    feed = os.path.join(cwd, "files", "menu.json")
    configure_logging()
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 YaBrowser/18.10.2.172 Yowser/2.5 Safari/537.36',
        'DOWNLOAD_DELAY': 2,
        'FEED_FORMAT': "jsonlines",
        'FEED_URI': "file:///{}".format(feed),
        "COOKIES_DEBUG": True
    })

    process.crawl(CrosspackSpider)
    process.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
