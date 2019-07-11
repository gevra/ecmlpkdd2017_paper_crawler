import scrapy
from scrapy.http import Request


class PaperSpider(scrapy.Spider):
    name = "ecml_paper"

    start_urls = ["http://ecmlpkdd2017.ijs.si/program.html"]

    def parse(self, response):
        def parse_paper(paper):
            if paper.css('div.panel-body a.aaa::attr(href)').extract_first():
                url = str(paper.css('div.panel-body a.aaa::attr(href)').extract_first()).strip()
            else:
                url = str(paper.css('div.panel-body a::attr(href)').extract_first()).strip().replace("article", "content/pdf") + ".pdf"
            return {
                'title': str(paper.css('div.panel-heading a h4.panel-title::text').extract_first() or '').strip(),
                'authors': str(paper.css('div.panel-heading a p::text').extract_first() or '').strip(),
                'session': str(paper.css('div.panel-heading a p em::text').extract_first() or '').strip(),
                'abstract': str(paper.css('div.panel-body p::text').extract_first() or '').strip(),
                'url': url,
                'tag': str(paper.css('div.panel-heading a span.label::text').extract_first() or '').strip(),
            }

        for paper in response.css('div.panel'):
            paper_data = parse_paper(paper)
            # print("\n%s\n" % paper_data)
            yield Request(
                url=response.urljoin(paper_data['url']),
                meta=paper_data,
                callback=self.save_pdf
            )

    def save_pdf(self, response):
        path = "papers/" + response.url.split('/')[-1]
        self.logger.info('Saving PDF %s', path)
        with open(path, 'wb') as f:
            f.write(response.body)
        yield {
                'title': response.meta['title'],
                'authors': response.meta['authors'],
                'session': response.meta['session'],
                'abstract': response.meta['abstract'],
                'url': response.meta['url'],
                'tag': response.meta['tag'],
            }
