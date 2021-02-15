import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from creditsuisse.items import Article


class CreditSpider(scrapy.Spider):
    name = 'credit'
    start_urls = ['https://www.credit-suisse.com/uk/en/insights.html']

    def parse(self, response):
        links = response.xpath('//article//a[@class="a-link"]/@href').getall()
        yield from response.follow_all(links, self.parse_related)

    def parse_related(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)

        related = response.xpath('//li[@class="mod_related_articles_list_item"]//a[@class="a-link"]/@href').getall()
        yield from response.follow_all(related, self.parse_related)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="mod_article_header_title"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d.%m.%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="component_standard"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
