import scrapy
from scrapy.http import Response

from config import technologies_from_vacancies, positions_for_scraping


class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["djinni.co"]
    start_urls = positions_for_scraping

    def parse(self, response: Response, **kwargs):
        for job in response.css("li.list-jobs__item"):
            detailed_url = response.urljoin(
                job.css("a.job-list-item__link::attr(href)").get()
            )
            yield response.follow(
                detailed_url,
                callback=self._parse_detailed_page,
            )

        next_page = response.css(
            "li.page-item.active + li.page-item a.page-link::attr(href)"
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_detailed_page(response: Response):
        title = response.css("div.detail--title-wrapper h1::text").get().strip()
        salary = response.css(".public-salary-item::text").re_first(r"\$(\d+)")
        company = response.css("a.job-details--title::text").get().strip()
        if salary:
            salary = int(salary)
        else:
            salary = None
        description = response.css("div.col-sm-8").get()
        views = int(response.css("p.text-muted").re_first(r"(\d+) перегляд"))
        applications = int(response.css("p.text-muted").re_first(r"(\d+) відгук"))
        experience = int(
            response.css('div.job-additional-info--item-text:contains("досвіду")::text')
            .get()
            .split()[0]
            .replace("Без", "0")
        )
        location = [
            country.strip()
            for country in response.css("div.job-additional-info span.location-text::text")
            .get()
            .strip()
            .replace("\n", "")
            .split(",")
        ]
        found_technologies = []
        for technology in technologies_from_vacancies:
            if technology.lower() in description.lower():
                found_technologies.append(technology)
        yield {
            "title": title,
            "salary": salary,
            "company": company,
            "location": list(location),
            "views": views,
            "applications": applications,
            "found_technologies": found_technologies,
            "experience": experience,
        }
