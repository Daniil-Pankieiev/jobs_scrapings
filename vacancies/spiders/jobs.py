import scrapy
from scrapy.http import Response

from config import technologies_from_vacancies, positions_for_scraping


class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["djinni.co"]
    start_urls = positions_for_scraping

    def parse(self, response: Response, **kwargs):
        pass